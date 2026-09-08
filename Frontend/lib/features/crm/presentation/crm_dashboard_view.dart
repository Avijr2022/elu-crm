import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/edition/edition_controller.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/customer_service.dart';
import '../data/lead_service.dart';
import '../data/opportunity_service.dart';

class CrmDashboardView extends StatefulWidget {
  const CrmDashboardView({super.key, required this.profile});

  final Map<String, dynamic> profile;

  @override
  State<CrmDashboardView> createState() => _CrmDashboardViewState();
}

class _CrmDashboardViewState extends State<CrmDashboardView> {
  final _leads = LeadService();
  final _opps = OpportunityService();
  final _customers = CustomerService();
  bool _loading = true;
  String? _error;
  int _leadTotal = 0;
  int _openOppTotal = 0;
  int _wonOppTotal = 0;
  int _activeCustomerTotal = 0;
  double _pipelineValue = 0;
  double _weightedValue = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    final edition = context.read<EditionController>();
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final leadRes = await _leads.list(pageSize: 1);
      var openOpp = 0;
      var wonOpp = 0;
      var activeCustomers = 0;
      var pipeValue = 0.0;
      var weighted = 0.0;

      if (edition.hasOpportunity) {
        final openRes = await _opps.list(pageSize: 1, status: 'OPEN');
        final wonRes = await _opps.list(pageSize: 1, status: 'CLOSED_WON');
        final pipe = await _opps.pipeline();
        openOpp = openRes.total;
        wonOpp = wonRes.total;
        for (final b in pipe.stages) {
          pipeValue += b.totalValue;
          weighted += b.weightedValue;
        }
      }
      if (edition.hasCustomer) {
        final activeRes =
            await _customers.list(page: 1, pageSize: 1, status: 'ACTIVE');
        activeCustomers = activeRes.total;
      }

      if (!mounted) return;
      setState(() {
        _leadTotal = leadRes.total;
        _openOppTotal = openOpp;
        _wonOppTotal = wonOpp;
        _activeCustomerTotal = activeCustomers;
        _pipelineValue = pipeValue;
        _weightedValue = weighted;
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

  String _inr(double v) {
    final f = v.toStringAsFixed(v == v.roundToDouble() ? 0 : 2);
    return '₹ $f';
  }

  @override
  Widget build(BuildContext context) {
    final edition = context.watch<EditionController>();
    final hasOpp = edition.hasOpportunity;
    final hasCustomer = edition.hasCustomer;

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(CrmSpacing.lg),
        children: [
          Text(
            'Welcome, ${widget.profile['display_name'] ?? ''}',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: CrmSpacing.lg),
          if (_loading)
            const Center(child: CircularProgressIndicator())
          else if (_error != null)
            Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error))
          else ...[
            _KpiRow(
              children: [
                _KpiCard(label: 'Leads', value: '$_leadTotal'),
                if (hasOpp)
                  _KpiCard(label: 'Open', value: '$_openOppTotal')
                else if (hasCustomer)
                  _KpiCard(label: 'Active customers', value: '$_activeCustomerTotal'),
              ],
            ),
            if (hasOpp) ...[
              const SizedBox(height: CrmSpacing.sm),
              _KpiRow(
                children: [
                  _KpiCard(label: 'Closed won', value: '$_wonOppTotal'),
                  _KpiCard(label: 'Pipeline value', value: _inr(_pipelineValue)),
                ],
              ),
              const SizedBox(height: CrmSpacing.sm),
              _KpiCard(label: 'Weighted forecast', value: _inr(_weightedValue)),
              if (hasCustomer) ...[
                const SizedBox(height: CrmSpacing.sm),
                _KpiCard(
                  label: 'Active customers',
                  value: '$_activeCustomerTotal',
                ),
              ],
            ],
          ],
          const SizedBox(height: CrmSpacing.lg),
          Card(
            child: ListTile(
              leading: const Icon(Icons.route_outlined),
              title: const Text('L2C Demo Journey'),
              subtitle: Text(
                hasOpp
                    ? 'Guided UAT: Lead → Close Won → Active Customer'
                    : 'Guided UAT: Lead → Customer → Active',
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.push(CrmRoutes.l2cDemo),
            ),
          ),
          const SizedBox(height: CrmSpacing.lg),
          Text('Account', style: Theme.of(context).textTheme.titleMedium),
          _tile('Tenant', '${widget.profile['tenant_name']} (${widget.profile['tenant_code']})'),
          _tile('Role', '${widget.profile['role_name']}'),
          _tile('Organization', '${widget.profile['organization_name']}'),
          ListTile(
            leading: const Icon(Icons.branding_watermark_outlined),
            title: const Text('Tenant branding'),
            subtitle: const Text('Logo for quotation PDFs'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.push(CrmRoutes.tenantBranding),
          ),
        ],
      ),
    );
  }

  Widget _tile(String k, String v) => ListTile(dense: true, title: Text(k), subtitle: Text(v));
}

class _KpiRow extends StatelessWidget {
  const _KpiRow({required this.children});
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        for (var i = 0; i < children.length; i++) ...[
          if (i > 0) const SizedBox(width: CrmSpacing.sm),
          Expanded(child: children[i]),
        ],
      ],
    );
  }
}

class _KpiCard extends StatelessWidget {
  const _KpiCard({
    required this.label,
    required this.value,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(CrmSpacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 4),
            Text(value, style: Theme.of(context).textTheme.titleLarge),
          ],
        ),
      ),
    );
  }
}
