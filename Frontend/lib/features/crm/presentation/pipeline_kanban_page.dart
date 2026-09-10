import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/auth/crm_rbac.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/lookup_service.dart';
import '../data/opportunity_model.dart';
import '../data/opportunity_service.dart';

class PipelineKanbanPage extends StatefulWidget {
  const PipelineKanbanPage({super.key});

  @override
  State<PipelineKanbanPage> createState() => _PipelineKanbanPageState();
}

class _PipelineKanbanPageState extends State<PipelineKanbanPage> {
  final _service = OpportunityService();
  bool _loading = true;
  String? _error;
  PipelineResult? _pipeline;
  List<String> _stages = [];
  Map<String, String> _stageNames = {};

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final lookups = LookupService();
      final p = await _service.pipeline();
      final stages = await lookups.pipelineStageCodes();
      List<OpportunityStage> stageRows = const [];
      try {
        stageRows = await lookups.listOpportunityStages(includeInactive: false);
      } catch (_) {
        // Stage labels fall back to code formatting when lookup API unavailable.
      }
      if (!mounted) return;
      setState(() {
        _pipeline = p;
        _stages = stages;
        _stageNames = {for (final s in stageRows) s.code: s.name};
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

  String? _nextStage(String current) => nextPipelineStage(_stages, current);

  Future<void> _onDrop(Opportunity opp, String targetStage) async {
    final next = _nextStage(opp.stage);
    if (targetStage != next) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            next == null
                ? 'Already at final pipeline stage'
                : 'Advance one stage at a time → ${next.replaceAll('_', ' ')}',
          ),
        ),
      );
      return;
    }
    try {
      await _service.advanceStage(
        opportunityId: opp.opportunityId,
        stage: targetStage,
      );
      await _load();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Stage advanced')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  String _inr(double v) {
    final f = v.toStringAsFixed(v == v.roundToDouble() ? 0 : 2);
    return '₹ $f';
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
            TextButton(onPressed: _load, child: const Text('Retry')),
          ],
        ),
      );
    }
    final stages = _pipeline!.stages;
    final h = MediaQuery.sizeOf(context).height - 200;
    final profile = context.watch<AuthController>().profile;
    final canManage = CrmRbac.isManager(profile?['role_code'] as String?);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (canManage)
          Padding(
            padding: const EdgeInsets.fromLTRB(CrmSpacing.page, CrmSpacing.sm, CrmSpacing.page, 0),
            child: Align(
              alignment: Alignment.centerRight,
              child: Wrap(
                spacing: CrmSpacing.sm,
                children: [
                  TextButton.icon(
                    onPressed: () => context.push(CrmRoutes.activityTypes),
                    icon: const Icon(Icons.category_outlined, size: 18),
                    label: const Text('Types'),
                  ),
                  TextButton.icon(
                    onPressed: () => context.push(CrmRoutes.activityOutcomes),
                    icon: const Icon(Icons.checklist_outlined, size: 18),
                    label: const Text('Outcomes'),
                  ),
                  TextButton.icon(
                    onPressed: () => context.push(CrmRoutes.opportunityStages),
                    icon: const Icon(Icons.tune_outlined, size: 18),
                    label: const Text('Manage stages'),
                  ),
                ],
              ),
            ),
          ),
        Expanded(
          child: RefreshIndicator(
      onRefresh: _load,
      child: SizedBox(
        height: h,
        child: ListView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.all(CrmSpacing.page),
          children: [
            for (final bucket in stages)
              SizedBox(
                height: h,
                child: _StageColumn(
                  bucket: bucket,
                  stageLabel: _stageNames[bucket.stage] ?? bucket.stage.replaceAll('_', ' '),
                  formatValue: _inr,
                  onOpen: (id) => context
                      .push(CrmRoutes.opportunityDetail(id))
                      .then((_) => _load()),
                  onDrop: _onDrop,
                ),
              ),
          ],
        ),
      ),
    ),
        ),
      ],
    );
  }
}

class _StageColumn extends StatelessWidget {
  const _StageColumn({
    required this.bucket,
    required this.stageLabel,
    required this.formatValue,
    required this.onOpen,
    required this.onDrop,
  });

  final PipelineStageBucket bucket;
  final String stageLabel;
  final String Function(double) formatValue;
  final Future<void> Function(String) onOpen;
  final Future<void> Function(Opportunity, String) onDrop;

  @override
  Widget build(BuildContext context) {
    return DragTarget<Opportunity>(
      onWillAcceptWithDetails: (d) =>
          !d.data.isTerminal && d.data.status != 'ON_HOLD',
      onAcceptWithDetails: (d) => onDrop(d.data, bucket.stage),
      builder: (context, candidate, rejected) {
        return Container(
          width: 280,
          margin: const EdgeInsets.only(right: CrmSpacing.sm),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(CrmRadii.card),
            color: candidate.isNotEmpty
                ? Theme.of(context).colorScheme.primaryContainer.withOpacity(0.3)
                : null,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: CrmSpacing.xs),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      stageLabel,
                      style: Theme.of(context).textTheme.titleSmall,
                    ),
                    Text(
                      '${bucket.count} · ${formatValue(bucket.totalValue)}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: CrmSpacing.xs),
              Expanded(
                child: bucket.items.isEmpty
                    ? const Center(child: Text('—'))
                    : ListView.builder(
                        itemCount: bucket.items.length,
                        itemBuilder: (context, i) {
                          final o = bucket.items[i];
                          final card = Card(
                            margin: const EdgeInsets.only(
                              bottom: CrmSpacing.xs,
                              left: CrmSpacing.xs,
                              right: CrmSpacing.xs,
                            ),
                            child: ListTile(
                              dense: true,
                              title: Text(o.name,
                                  maxLines: 2, overflow: TextOverflow.ellipsis),
                              subtitle: Text(
                                '${o.companyName ?? '—'}\n${formatValue(o.opportunityValue)} · ${o.probability}%',
                              ),
                              isThreeLine: true,
                              onTap: () => onOpen(o.opportunityId),
                            ),
                          );
                          if (o.isTerminal || o.status == 'ON_HOLD') {
                            return card;
                          }
                          return LongPressDraggable<Opportunity>(
                            data: o,
                            feedback: Material(
                              elevation: 4,
                              child: SizedBox(
                                width: 260,
                                child: card,
                              ),
                            ),
                            childWhenDragging: Opacity(opacity: 0.4, child: card),
                            child: card,
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
