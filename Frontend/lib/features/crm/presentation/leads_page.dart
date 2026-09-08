import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/auth/crm_rbac.dart';
import '../../../core/edition/edition_controller.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_search_field.dart';
import '../../../core/widgets/crm_status_chip.dart';
import '../data/lead_model.dart';
import 'leads_controller.dart';

class LeadsPage extends StatefulWidget {
  const LeadsPage({super.key});

  @override
  State<LeadsPage> createState() => _LeadsPageState();
}

class _LeadsPageState extends State<LeadsPage> {
  late final LeadsController _controller;
  final _searchCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _controller = LeadsController()..load();
  }

  @override
  void dispose() {
    _controller.dispose();
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _openCreate() async {
    final created = await context.push<bool>(CrmRoutes.leadsNew);
    if (!mounted) return;
    if (created == true) {
      await _controller.load();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Lead created')),
      );
    }
  }

  Future<void> _convert(Lead lead) async {
    final number = await _controller.convertLead(lead);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          number != null
              ? 'Converted to $number'
              : (_controller.error ?? 'Convert failed'),
        ),
      ),
    );
  }

  Future<void> _openDetail(Lead lead) async {
    await context.push(CrmRoutes.leadDetail(lead.leadId));
    if (mounted) await _controller.load();
  }

  String _formatInr(double value) {
    final fixed = value.toStringAsFixed(value == value.roundToDouble() ? 0 : 2);
    return '₹ $fixed';
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        final profile = context.watch<AuthController>().profile;
        final edition = context.watch<EditionController>();
                  final canConvert = CrmRbac.canConvertLead(
                    profile,
                    hasOpportunityEdition: edition.hasOpportunity,
                    hasCustomerEdition: edition.hasCustomer,
                  );
        return Padding(
          padding: const EdgeInsets.all(CrmSpacing.page),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              LayoutBuilder(
                builder: (context, constraints) {
                  final wide = constraints.maxWidth > 700;
                  void runSearch() {
                    _controller.search = _searchCtrl.text.trim();
                    _controller.load();
                  }

                  final search = CrmSearchField(
                    controller: _searchCtrl,
                    hintText: 'Search name, company, email, number',
                    onSearch: runSearch,
                  );
                  final canCreate = CrmRbac.canCreateLead(profile);
                  final addBtn = canCreate
                      ? FilledButton.icon(
                          onPressed: _openCreate,
                          icon: const Icon(Icons.add),
                          label: const Text('Add New Lead'),
                        )
                      : null;
                  if (wide) {
                    return Row(
                      children: [
                        Expanded(child: search),
                        if (addBtn != null) ...[
                          const SizedBox(width: CrmSpacing.sm),
                          addBtn,
                        ],
                      ],
                    );
                  }
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      search,
                      if (addBtn != null) ...[
                        const SizedBox(height: CrmSpacing.sm),
                        Align(alignment: Alignment.centerRight, child: addBtn),
                      ],
                    ],
                  );
                },
              ),
              const SizedBox(height: CrmSpacing.sm),
              Text(
                '${_controller.total} lead(s)',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: CrmSpacing.xs),
              if (_controller.error != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Text(
                    _controller.error!,
                    style: TextStyle(color: Theme.of(context).colorScheme.error),
                  ),
                ),
              Expanded(
                child: _controller.loading
                    ? const Center(child: CircularProgressIndicator())
                    : LayoutBuilder(
                        builder: (context, constraints) {
                          final wide = constraints.maxWidth > 700;
                          if (wide) {
                            return _LeadsTable(
                              items: _controller.items,
                              formatValue: _formatInr,
                              onConvert: canConvert ? _convert : null,
                              onOpen: _openDetail,
                              onRefresh: _controller.load,
                            );
                          }
                          return _LeadsCardList(
                            items: _controller.items,
                            formatValue: _formatInr,
                            onConvert: canConvert ? _convert : null,
                            onOpen: _openDetail,
                            onRefresh: _controller.load,
                          );
                        },
                      ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _LeadsCardList extends StatelessWidget {
  const _LeadsCardList({
    required this.items,
    required this.formatValue,
    this.onConvert,
    required this.onOpen,
    required this.onRefresh,
  });

  final List<Lead> items;
  final String Function(double) formatValue;
  final Future<void> Function(Lead)? onConvert;
  final Future<void> Function(Lead) onOpen;
  final Future<void> Function() onRefresh;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('No leads yet'),
            const SizedBox(height: CrmSpacing.xs),
            TextButton.icon(
              onPressed: onRefresh,
              icon: const Icon(Icons.refresh),
              label: const Text('Refresh'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: onRefresh,
      child: ListView.separated(
        physics: const AlwaysScrollableScrollPhysics(),
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(height: CrmSpacing.sm),
        itemBuilder: (context, index) {
          final lead = items[index];
          return _LeadCard(
            lead: lead,
            formatValue: formatValue,
            onTap: () => onOpen(lead),
            onConvert: lead.isTerminal || onConvert == null
                ? null
                : () => onConvert!(lead),
          );
        },
      ),
    );
  }
}

class _LeadCard extends StatelessWidget {
  const _LeadCard({
    required this.lead,
    required this.formatValue,
    required this.onTap,
    this.onConvert,
  });

  final Lead lead;
  final String Function(double) formatValue;
  final VoidCallback onTap;
  final VoidCallback? onConvert;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(CrmRadii.card),
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(CrmSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      lead.fullName,
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ),
                  CrmStatusChip(status: lead.status),
                ],
              ),
              const SizedBox(height: CrmSpacing.xs),
              Text(
                lead.leadNumber,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: scheme.onSurfaceVariant,
                    ),
              ),
              if (lead.companyName != null && lead.companyName!.isNotEmpty) ...[
                const SizedBox(height: CrmSpacing.xs),
                Row(
                  children: [
                    Icon(Icons.business_outlined,
                        size: 16, color: scheme.outline),
                    const SizedBox(width: 4),
                    Expanded(child: Text(lead.companyName!)),
                  ],
                ),
              ],
              if (lead.email != null && lead.email!.isNotEmpty) ...[
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(Icons.mail_outline, size: 16, color: scheme.outline),
                    const SizedBox(width: 4),
                    Expanded(child: Text(lead.email!)),
                  ],
                ),
              ],
              if (lead.phone != null && lead.phone!.isNotEmpty) ...[
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(Icons.phone_outlined, size: 16, color: scheme.outline),
                    const SizedBox(width: 4),
                    Expanded(child: Text(lead.phone!)),
                  ],
                ),
              ],
              const SizedBox(height: CrmSpacing.sm),
              Row(
                children: [
                  Text(
                    formatValue(lead.estimatedValue),
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  const Spacer(),
                  if (onConvert != null)
                    TextButton(
                      onPressed: onConvert,
                      child: const Text('Convert'),
                    ),
                  Icon(Icons.chevron_right, color: scheme.outline),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _LeadsTable extends StatelessWidget {
  const _LeadsTable({
    required this.items,
    required this.formatValue,
    this.onConvert,
    required this.onOpen,
    required this.onRefresh,
  });

  final List<Lead> items;
  final String Function(double) formatValue;
  final Future<void> Function(Lead)? onConvert;
  final Future<void> Function(Lead) onOpen;
  final Future<void> Function() onRefresh;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('No leads yet'),
            const SizedBox(height: 8),
            TextButton.icon(
              onPressed: onRefresh,
              icon: const Icon(Icons.refresh),
              label: const Text('Refresh'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: onRefresh,
      child: LayoutBuilder(
        builder: (context, constraints) {
          return SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: ConstrainedBox(
                constraints: BoxConstraints(minWidth: constraints.maxWidth),
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('Lead #')),
                    DataColumn(label: Text('Full Name')),
                    DataColumn(label: Text('Company')),
                    DataColumn(label: Text('Email')),
                    DataColumn(label: Text('Phone')),
                    DataColumn(label: Text('Status')),
                    DataColumn(label: Text('Est. Value'), numeric: true),
                    DataColumn(label: Text('Action')),
                  ],
                  rows: [
                    for (final lead in items)
                      DataRow(
                        onSelectChanged: (_) => onOpen(lead),
                        cells: [
                          DataCell(Text(lead.leadNumber)),
                          DataCell(Text(lead.fullName)),
                          DataCell(Text(lead.companyName ?? '—')),
                          DataCell(Text(lead.email ?? '—')),
                          DataCell(Text(lead.phone ?? '—')),
                          DataCell(CrmStatusChip(status: lead.status)),
                          DataCell(Text(formatValue(lead.estimatedValue))),
                          DataCell(
                            lead.isTerminal || onConvert == null
                                ? const Text('—')
                                : TextButton(
                                    onPressed: () => onConvert!(lead),
                                    child: const Text('Convert'),
                                  ),
                          ),
                        ],
                      ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
