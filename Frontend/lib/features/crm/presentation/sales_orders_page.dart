import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_status_chip.dart';
import '../data/customer_service.dart';
import '../data/opportunity_model.dart';
import '../data/opportunity_service.dart';
import '../data/sales_order_service.dart';

class SalesOrdersPage extends StatefulWidget {
  const SalesOrdersPage({
    super.key,
    this.opportunityId,
    this.customerId,
    this.status,
  });

  final String? opportunityId;
  final String? customerId;
  final String? status;

  @override
  State<SalesOrdersPage> createState() => _SalesOrdersPageState();
}

class _SalesOrdersPageState extends State<SalesOrdersPage> {
  final _service = SalesOrderService();
  final _oppService = OpportunityService();
  final _custService = CustomerService();
  String? _statusFilter;
  String? _selectedOppId;
  String? _selectedCustId;
  List<Opportunity> _opportunities = [];
  List<Customer> _customers = [];
  bool _loading = true;
  String? _error;
  List<SalesOrder> _items = [];

  @override
  void initState() {
    super.initState();
    _selectedOppId = _emptyToNull(widget.opportunityId);
    _selectedCustId = _emptyToNull(widget.customerId);
    _statusFilter = widget.status;
    _loadFilterOptions();
    _load();
  }

  @override
  void didUpdateWidget(covariant SalesOrdersPage oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.opportunityId != widget.opportunityId ||
        oldWidget.customerId != widget.customerId ||
        oldWidget.status != widget.status) {
      _selectedOppId = _emptyToNull(widget.opportunityId);
      _selectedCustId = _emptyToNull(widget.customerId);
      _statusFilter = widget.status;
      _load();
    }
  }

  String? _emptyToNull(String? value) =>
      value == null || value.trim().isEmpty ? null : value.trim();

  Future<void> _loadFilterOptions() async {
    try {
      final opps = await _oppService.list(pageSize: 100);
      final custs = await _custService.list(page: 1, pageSize: 100);
      if (!mounted) return;
      setState(() {
        _opportunities = opps.items;
        _customers = custs.items;
      });
    } catch (_) {}
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final r = await _service.list(
        status: _statusFilter,
        opportunityId: _selectedOppId,
        customerId: _selectedCustId,
      );
      if (!mounted) return;
      setState(() {
        _items = r.items;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  void _applyFilters() {
    context.go(
      CrmRoutes.salesOrdersFiltered(
        opportunityId: _selectedOppId,
        customerId: _selectedCustId,
        status: _statusFilter,
      ),
    );
    _load();
  }

  void _clearFilters() {
    setState(() {
      _selectedOppId = null;
      _selectedCustId = null;
      _statusFilter = null;
    });
    context.go(CrmRoutes.salesOrders);
    _load();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading && _items.isEmpty) {
      return Column(
        children: [
          _filterBar(),
          const Expanded(child: Center(child: CircularProgressIndicator())),
        ],
      );
    }
    if (_error != null && _items.isEmpty) {
      return Column(
        children: [
          _filterBar(),
          Expanded(
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                  TextButton(onPressed: _load, child: const Text('Retry')),
                ],
              ),
            ),
          ),
        ],
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _filterBar(),
        Expanded(
          child: RefreshIndicator(
            onRefresh: _load,
            child: _items.isEmpty
                ? ListView(children: const [
                    SizedBox(height: 120),
                    Center(child: Text('No sales orders')),
                  ])
                : ListView.separated(
                    padding: const EdgeInsets.all(CrmSpacing.page),
                    itemCount: _items.length,
                    separatorBuilder: (_, __) => const SizedBox(height: CrmSpacing.sm),
                    itemBuilder: (_, i) {
                      final so = _items[i];
                      final contextLine = [
                        if (so.opportunityName != null) so.opportunityName,
                        if (so.customerName != null) so.customerName,
                      ].whereType<String>().join(' · ');
                      return Card(
                        child: ListTile(
                          title: Text(so.soNumber),
                          subtitle: Text(
                            contextLine.isEmpty
                                ? '${so.currencyCode} ${so.grandTotal}'
                                : '$contextLine\n${so.currencyCode} ${so.grandTotal}',
                          ),
                          isThreeLine: contextLine.isNotEmpty,
                          trailing: CrmStatusChip(status: so.status),
                          onTap: () => context.push(CrmRoutes.salesOrderDetail(so.salesOrderId)),
                        ),
                      );
                    },
                  ),
          ),
        ),
      ],
    );
  }

  Widget _filterBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(CrmSpacing.page, CrmSpacing.page, CrmSpacing.page, 0),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(CrmSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Filters', style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: CrmSpacing.sm),
              DropdownButtonFormField<String?>(
                value: _statusFilter,
                decoration: const InputDecoration(labelText: 'Status', isDense: true),
                items: const [
                  DropdownMenuItem(value: null, child: Text('All')),
                  DropdownMenuItem(value: 'DRAFT', child: Text('DRAFT')),
                  DropdownMenuItem(value: 'CONFIRMED', child: Text('CONFIRMED')),
                ],
                onChanged: (v) => setState(() => _statusFilter = v),
              ),
              const SizedBox(height: CrmSpacing.sm),
              DropdownButtonFormField<String?>(
                value: _selectedOppId,
                decoration: const InputDecoration(labelText: 'Opportunity', isDense: true),
                items: [
                  const DropdownMenuItem(value: null, child: Text('All opportunities')),
                  ..._opportunities.map(
                    (o) => DropdownMenuItem(
                      value: o.opportunityId,
                      child: Text(o.name, overflow: TextOverflow.ellipsis),
                    ),
                  ),
                ],
                onChanged: (v) => setState(() => _selectedOppId = v),
              ),
              const SizedBox(height: CrmSpacing.sm),
              DropdownButtonFormField<String?>(
                value: _selectedCustId,
                decoration: const InputDecoration(labelText: 'Customer', isDense: true),
                items: [
                  const DropdownMenuItem(value: null, child: Text('All customers')),
                  ..._customers.map(
                    (c) => DropdownMenuItem(
                      value: c.customerId,
                      child: Text(c.legalName, overflow: TextOverflow.ellipsis),
                    ),
                  ),
                ],
                onChanged: (v) => setState(() => _selectedCustId = v),
              ),
              const SizedBox(height: CrmSpacing.sm),
              Row(
                children: [
                  FilledButton(onPressed: _applyFilters, child: const Text('Apply')),
                  const SizedBox(width: CrmSpacing.sm),
                  TextButton(onPressed: _clearFilters, child: const Text('Clear')),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
