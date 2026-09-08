import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/auth/crm_rbac.dart';
import '../../../core/edition/edition_controller.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_section_card.dart';
import '../data/lead_model.dart';
import 'lead_detail_controller.dart';
import 'activity_timeline_page.dart';
import 'widgets/lead_detail_header.dart';

class LeadDetailPage extends StatefulWidget {
  const LeadDetailPage({super.key, required this.leadId});

  final String leadId;

  @override
  State<LeadDetailPage> createState() => _LeadDetailPageState();
}

class _LeadDetailPageState extends State<LeadDetailPage>
    with SingleTickerProviderStateMixin {
  late final LeadDetailController _controller;
  late final TabController _tabs;

  @override
  void initState() {
    super.initState();
    _controller = LeadDetailController(leadId: widget.leadId)..load();
    _tabs = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabs.dispose();
    _controller.dispose();
    super.dispose();
  }

  Future<void> _openEdit(Lead lead) async {
    final saved = await context.push<bool>(CrmRoutes.leadEdit(lead.leadId));
    if (!mounted) return;
    if (saved == true) {
      await _controller.load();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Lead updated')),
      );
    }
  }

  Future<void> _convert() async {
    final number = await _controller.convert();
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

  Future<void> _qualify() async {
    final ok = await _controller.qualify();
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(ok ? 'Lead qualified' : (_controller.error ?? 'Qualify failed'))),
    );
  }

  Future<void> _disqualify() async {
    final reason = TextEditingController();
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Disqualify lead'),
        content: TextField(
          controller: reason,
          decoration: const InputDecoration(labelText: 'Reason *'),
          maxLines: 2,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (reason.text.trim().isEmpty) return;
              Navigator.pop(ctx, true);
            },
            child: const Text('Disqualify'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) {
      reason.dispose();
      return;
    }
    final ok = await _controller.disqualify(reason.text.trim());
    reason.dispose();
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(ok ? 'Lead disqualified' : (_controller.error ?? 'Disqualify failed'))),
    );
  }

  String _formatValue(Lead lead) {
    final symbol = lead.currencyCode == 'INR' ? '₹' : lead.currencyCode;
    final fixed = lead.estimatedValue.toStringAsFixed(
      lead.estimatedValue == lead.estimatedValue.roundToDouble() ? 0 : 2,
    );
    return '$symbol $fixed';
  }

  String _formatDate(DateTime? dt) {
    if (dt == null) return '—';
    return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-'
        '${dt.day.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        final lead = _controller.lead;
        final profile = context.watch<AuthController>().profile;
        final edition = context.watch<EditionController>();
        final canConvert = lead != null &&
            !lead.isTerminal &&
            CrmRbac.canConvertLead(
              profile,
              hasOpportunityEdition: edition.hasOpportunity,
              hasCustomerEdition: edition.hasCustomer,
            );
        final canQualify = lead != null &&
            lead.canQualify &&
            CrmRbac.canQualifyLead(profile);
        final canDisqualify = lead != null &&
            lead.canDisqualify &&
            CrmRbac.canDisqualifyLead(profile);
        return Scaffold(
          appBar: AppBar(
            title: Text(lead?.leadNumber ?? 'Lead'),
            actions: [
              if (lead != null)
                IconButton(
                  tooltip: 'Edit',
                  onPressed: () => _openEdit(lead),
                  icon: const Icon(Icons.edit_outlined),
                ),
              if (canQualify)
                TextButton(
                  onPressed: _controller.qualifying ? null : _qualify,
                  child: _controller.qualifying
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Qualify'),
                ),
              if (canDisqualify)
                TextButton(
                  onPressed: _controller.disqualifying ? null : _disqualify,
                  child: const Text('Disqualify'),
                ),
              if (canConvert)
                TextButton(
                  onPressed: _controller.converting ? null : _convert,
                  child: _controller.converting
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Convert'),
                ),
              IconButton(
                tooltip: 'Refresh',
                onPressed: _controller.loading ? null : _controller.load,
                icon: const Icon(Icons.refresh),
              ),
            ],
            bottom: lead == null
                ? null
                : TabBar(
                    controller: _tabs,
                    tabs: const [
                      Tab(text: 'Overview'),
                      Tab(text: 'Activity'),
                    ],
                  ),
          ),
          body: _buildBody(lead),
        );
      },
    );
  }

  Widget _buildBody(Lead? lead) {
    if (_controller.loading && lead == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_controller.error != null && lead == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(CrmSpacing.lg),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                _controller.error!,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.error,
                ),
              ),
              const SizedBox(height: CrmSpacing.md),
              FilledButton.icon(
                onPressed: _controller.load,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }
    if (lead == null) {
      return const Center(child: Text('Lead not found'));
    }

    return Column(
      children: [
        LeadDetailHeader(lead: lead),
        if (_controller.error != null)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: CrmSpacing.page),
            child: Text(
              _controller.error!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ),
        Expanded(
          child: TabBarView(
            controller: _tabs,
            children: [
              RefreshIndicator(
                onRefresh: _controller.load,
                child: _OverviewTab(
                  lead: lead,
                  formatValue: _formatValue,
                  formatDate: _formatDate,
                ),
              ),
              ActivityTimelinePage(
                entityType: 'LEAD',
                entityId: lead.leadId,
                embedded: true,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _OverviewTab extends StatelessWidget {
  const _OverviewTab({
    required this.lead,
    required this.formatValue,
    required this.formatDate,
  });

  final Lead lead;
  final String Function(Lead) formatValue;
  final String Function(DateTime?) formatDate;

  @override
  Widget build(BuildContext context) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(
        CrmSpacing.page,
        0,
        CrmSpacing.page,
        CrmSpacing.lg,
      ),
      children: [
        CrmSectionCard(
          title: 'Contact',
          child: Column(
            children: [
              _kv('Email', lead.email),
              _kv('Phone', lead.phone),
              _kv('Company', lead.companyName),
            ],
          ),
        ),
        const SizedBox(height: CrmSpacing.sm),
        CrmSectionCard(
          title: 'Deal',
          child: Column(
            children: [
              _kv('Estimated value', formatValue(lead)),
              _kv('Created', formatDate(lead.createdOn)),
              _kv('Last modified', formatDate(lead.modifiedOn)),
              if (lead.ownerId != null) _kv('Owner ID', lead.ownerId),
            ],
          ),
        ),
        const SizedBox(height: CrmSpacing.sm),
        CrmSectionCard(
          title: 'Notes',
          child: Text(
            lead.notes?.isNotEmpty == true ? lead.notes! : 'No notes yet.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ),
        const SizedBox(height: CrmSpacing.sm),
        CrmSectionCard(
          title: 'Qualifiers',
          child: Text(
            'Qualification details will be available in a future release.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
          ),
        ),
        const SizedBox(height: CrmSpacing.sm),
        CrmSectionCard(
          title: 'Follow-up',
          child: Text(
            'Assignment and follow-up scheduling will be available in a future release.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
          ),
        ),
      ],
    );
  }

  Widget _kv(String label, String? value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: CrmSpacing.xs),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(child: Text(value?.isNotEmpty == true ? value! : '—')),
        ],
      ),
    );
  }
}
