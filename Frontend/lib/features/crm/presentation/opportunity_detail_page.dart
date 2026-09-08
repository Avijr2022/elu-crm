import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/auth/crm_rbac.dart';
import '../../../core/edition/edition_controller.dart';

import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_section_card.dart';
import '../data/handoff_service.dart';
import '../data/opportunity_model.dart';
import 'opportunity_detail_controller.dart';
import 'activity_timeline_page.dart';
import 'widgets/close_lost_wizard_dialog.dart';
import 'widgets/close_won_wizard_dialog.dart';
import 'widgets/opportunity_detail_header.dart';

class OpportunityDetailPage extends StatefulWidget {
  const OpportunityDetailPage({super.key, required this.opportunityId});

  final String opportunityId;

  @override
  State<OpportunityDetailPage> createState() => _OpportunityDetailPageState();
}

class _OpportunityDetailPageState extends State<OpportunityDetailPage>
    with SingleTickerProviderStateMixin {
  late final OpportunityDetailController _controller;
  late final TabController _tabs;

  @override
  void initState() {
    super.initState();
    _controller =
        OpportunityDetailController(opportunityId: widget.opportunityId)
          ..load();
    _tabs = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabs.dispose();
    _controller.dispose();
    super.dispose();
  }

  String _formatValue(Opportunity opp, {bool weighted = false}) {
    final symbol = opp.currencyCode == 'INR' ? '₹' : opp.currencyCode;
    final v = weighted ? opp.weightedValue : opp.opportunityValue;
    final fixed = v.toStringAsFixed(v == v.roundToDouble() ? 0 : 2);
    return '$symbol $fixed';
  }

  String _formatDate(DateTime? dt) {
    if (dt == null) return '—';
    return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-'
        '${dt.day.toString().padLeft(2, '0')}';
  }

  Future<void> _advance() async {
    final ok = await _controller.advance();
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          ok ? 'Advanced to next stage' : (_controller.error ?? 'Advance failed'),
        ),
      ),
    );
  }

  Future<void> _openEdit(Opportunity opp) async {
    final saved = await context.push<bool>(CrmRoutes.opportunityEdit(opp.opportunityId));
    if (!mounted) return;
    if (saved == true) {
      await _controller.load();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Opportunity updated')),
      );
    }
  }

  Future<void> _closeWon() async {
    final opp = _controller.opportunity;
    if (opp == null) return;
    final ok = await CloseWonWizardDialog.show(
      context,
      opportunity: opp,
      formatValue: (o) => _formatValue(o),
      onConfirm: ({closingNotes}) => _controller.closeWon(closingNotes: closingNotes),
    );
    if (!mounted || ok != true) return;
    var message = 'Closed won';
    if (context.read<EditionController>().hasPrjWo) {
      final handoff = await HandoffService().requestFromOpportunity(opp.opportunityId);
      if (handoff != null) message = 'Closed won · $handoff';
    }
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
    await _controller.load();
  }

  Future<void> _closeLost() async {
    final opp = _controller.opportunity;
    if (opp == null) return;
    final ok = await CloseLostWizardDialog.show(
      context,
      opportunity: opp,
      formatValue: (o) => _formatValue(o),
      onConfirm: (reason) => _controller.closeLost(reason),
    );
    if (!mounted || ok != true) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Closed lost')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        final opp = _controller.opportunity;
        final canAdvance = opp != null &&
            !opp.isTerminal &&
            opp.status != 'ON_HOLD' &&
            _controller.nextStage(opp.stage) != null;
        final profile = context.watch<AuthController>().profile;
        final canClose = opp != null && !opp.isTerminal && opp.status != 'ON_HOLD' && CrmRbac.canCloseWon(profile);
        return Scaffold(
          appBar: AppBar(
            title: Text(opp?.opportunityNumber ?? 'Opportunity'),
            actions: [
              if (opp != null && !opp.isTerminal)
                IconButton(
                  tooltip: 'Edit',
                  onPressed: () => _openEdit(opp),
                  icon: const Icon(Icons.edit_outlined),
                ),
              if (canAdvance)
                TextButton(
                  onPressed: _controller.advancing ? null : _advance,
                  child: _controller.advancing
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Advance'),
                ),
              if (canClose) ...[
                TextButton(onPressed: _controller.closing ? null : _closeWon, child: const Text('Won')),
                TextButton(onPressed: _controller.closing ? null : _closeLost, child: const Text('Lost')),
              ],
              IconButton(
                tooltip: 'Refresh',
                onPressed: _controller.loading ? null : _controller.load,
                icon: const Icon(Icons.refresh),
              ),
            ],
            bottom: opp == null
                ? null
                : TabBar(
                    controller: _tabs,
                    tabs: const [
                      Tab(text: 'Overview'),
                      Tab(text: 'Activity'),
                    ],
                  ),
          ),
          body: _buildBody(opp),
        );
      },
    );
  }

  Widget _buildBody(Opportunity? opp) {
    if (_controller.loading && opp == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_controller.error != null && opp == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(CrmSpacing.lg),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                _controller.error!,
                textAlign: TextAlign.center,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
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
    if (opp == null) {
      return const Center(child: Text('Opportunity not found'));
    }

    return Column(
      children: [
        OpportunityDetailHeader(
          opportunity: opp,
          formatValue: (o) => _formatValue(o),
          formatWeighted: (o) => _formatValue(o, weighted: true),
          formatDate: _formatDate,
        ),
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
                  opportunity: opp,
                  stages: _controller.stages,
                  stageNames: _controller.stageNames,
                  customerLabel: _controller.customerLabel,
                  formatValue: _formatValue,
                  formatDate: _formatDate,
                ),
              ),
              ActivityTimelinePage(
                entityType: 'OPPORTUNITY',
                entityId: opp.opportunityId,
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
    required this.opportunity,
    required this.stages,
    required this.stageNames,
    this.customerLabel,
    required this.formatValue,
    required this.formatDate,
  });

  final Opportunity opportunity;
  final List<String> stages;
  final Map<String, String> stageNames;
  final String? customerLabel;
  final String Function(Opportunity, {bool weighted}) formatValue;
  final String Function(DateTime?) formatDate;

  @override
  Widget build(BuildContext context) {
    final idx = stages.indexOf(opportunity.stage);
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(
        CrmSpacing.page,
        0,
        CrmSpacing.page,
        CrmSpacing.lg,
      ),
      children: [
        SizedBox(
          height: 36,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: stages.length,
            separatorBuilder: (_, __) => const SizedBox(width: 4),
            itemBuilder: (context, i) {
              final stage = stages[i];
              final label = stageNames[stage] ?? stage.replaceAll('_', ' ');
              final active = i <= idx;
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                decoration: BoxDecoration(
                  color: active
                      ? Theme.of(context).colorScheme.primary
                      : Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  label,
                  style: TextStyle(
                    fontSize: 11,
                    color: active
                        ? Theme.of(context).colorScheme.onPrimary
                        : Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: CrmSpacing.sm),
        CrmSectionCard(
          title: 'Deal',
          child: Column(
            children: [
              _kv('Status', opportunity.status.replaceAll('_', ' ')),
              _kv('Value', formatValue(opportunity)),
              _kv('Probability', '${opportunity.probability}%'),
              _kv('Weighted', formatValue(opportunity, weighted: true)),
              _kv('Expected close', formatDate(opportunity.expectedCloseDate)),
              _kv('Created', formatDate(opportunity.createdOn)),
              _kv('Modified', formatDate(opportunity.modifiedOn)),
              if (opportunity.lossReason != null)
                _kv('Loss reason', opportunity.lossReason),
            ],
          ),
        ),
        const SizedBox(height: CrmSpacing.sm),
        CrmSectionCard(
          title: 'Source',
          child: Column(
            children: [
              _kv('Source lead', opportunity.sourceLeadId ?? '—'),
              if (opportunity.customerId != null)
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Customer', style: TextStyle(fontWeight: FontWeight.w600)),
                  subtitle: Text(customerLabel ?? opportunity.customerId!),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => context.push(
                    CrmRoutes.customerDetail(opportunity.customerId!),
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: CrmSpacing.sm),
        if (context.watch<EditionController>().hasSalQuote)
          CrmSectionCard(
            title: 'Sales',
            child: ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.receipt_long_outlined),
              title: const Text('Sales orders'),
              subtitle: const Text('Orders linked to this opportunity'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => context.go(
                CrmRoutes.salesOrdersFiltered(opportunityId: opportunity.opportunityId),
              ),
            ),
          ),
        const SizedBox(height: CrmSpacing.sm),
        CrmSectionCard(
          title: 'Notes',
          child: Text(
            opportunity.notes?.isNotEmpty == true
                ? opportunity.notes!
                : 'No notes yet.',
            style: Theme.of(context).textTheme.bodyMedium,
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
