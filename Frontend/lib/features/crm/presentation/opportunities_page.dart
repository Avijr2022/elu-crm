import 'package:flutter/material.dart';

import '../data/opportunity_model.dart';
import 'opportunities_controller.dart';
import 'opportunity_form_dialog.dart';

class OpportunitiesPage extends StatefulWidget {
  const OpportunitiesPage({super.key});

  @override
  State<OpportunitiesPage> createState() => _OpportunitiesPageState();
}

class _OpportunitiesPageState extends State<OpportunitiesPage> {
  late final OpportunitiesController _controller;
  final _searchCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _controller = OpportunitiesController()..load();
  }

  @override
  void dispose() {
    _controller.dispose();
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _openCreate() async {
    final created = await showOpportunityFormDialog(context, _controller);
    if (created == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Opportunity created')),
      );
    }
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
        return Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              LayoutBuilder(
                builder: (context, constraints) {
                  final wide = constraints.maxWidth > 700;
                  final search = TextField(
                    controller: _searchCtrl,
                    decoration: InputDecoration(
                      hintText: 'Search name, company, number',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: IconButton(
                        onPressed: () {
                          _controller.search = _searchCtrl.text.trim();
                          _controller.load();
                        },
                        icon: const Icon(Icons.arrow_forward),
                      ),
                    ),
                    onSubmitted: (_) {
                      _controller.search = _searchCtrl.text.trim();
                      _controller.load();
                    },
                  );
                  final addBtn = FilledButton.icon(
                    onPressed: _openCreate,
                    icon: const Icon(Icons.add),
                    label: const Text('Add Opportunity'),
                  );
                  if (wide) {
                    return Row(
                      children: [
                        Expanded(child: search),
                        const SizedBox(width: 12),
                        addBtn,
                      ],
                    );
                  }
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      search,
                      const SizedBox(height: 12),
                      Align(alignment: Alignment.centerRight, child: addBtn),
                    ],
                  );
                },
              ),
              const SizedBox(height: 12),
              if (_controller.pipeline != null)
                SizedBox(
                  height: 88,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    children: [
                      for (final bucket in _controller.pipeline!.stages)
                        Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: FilterChip(
                            selected: _controller.stageFilter == bucket.stage,
                            label: Text(
                              '${bucket.stage.replaceAll('_', ' ')}\n'
                              '${bucket.count} · ${_formatInr(bucket.totalValue)}',
                            ),
                            onSelected: (selected) {
                              _controller.stageFilter =
                                  selected ? bucket.stage : null;
                              _controller.load();
                            },
                          ),
                        ),
                    ],
                  ),
                ),
              Text(
                '${_controller.total} opportunity(ies)',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 8),
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
                    : _OpportunitiesTable(
                        items: _controller.items,
                        formatValue: _formatInr,
                        nextStage: _controller.nextStage,
                        onAdvance: (opp) async {
                          final ok = await _controller.advance(opp);
                          if (!context.mounted) return;
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                ok
                                    ? 'Advanced to next stage'
                                    : (_controller.error ?? 'Advance failed'),
                              ),
                            ),
                          );
                        },
                        onRefresh: _controller.load,
                      ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _OpportunitiesTable extends StatelessWidget {
  const _OpportunitiesTable({
    required this.items,
    required this.formatValue,
    required this.nextStage,
    required this.onAdvance,
    required this.onRefresh,
  });

  final List<Opportunity> items;
  final String Function(double) formatValue;
  final String? Function(String) nextStage;
  final Future<void> Function(Opportunity) onAdvance;
  final Future<void> Function() onRefresh;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('No opportunities yet'),
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
                    DataColumn(label: Text('Opp #')),
                    DataColumn(label: Text('Name')),
                    DataColumn(label: Text('Company')),
                    DataColumn(label: Text('Stage')),
                    DataColumn(label: Text('Status')),
                    DataColumn(label: Text('Value'), numeric: true),
                    DataColumn(label: Text('Prob %'), numeric: true),
                    DataColumn(label: Text('Weighted'), numeric: true),
                    DataColumn(label: Text('Action')),
                  ],
                  rows: [
                    for (final opp in items)
                      DataRow(
                        cells: [
                          DataCell(Text(opp.opportunityNumber)),
                          DataCell(Text(opp.name)),
                          DataCell(Text(opp.companyName ?? '—')),
                          DataCell(Text(opp.stage.replaceAll('_', ' '))),
                          DataCell(Text(opp.status)),
                          DataCell(Text(formatValue(opp.opportunityValue))),
                          DataCell(Text('${opp.probability}')),
                          DataCell(Text(formatValue(opp.weightedValue))),
                          DataCell(
                            nextStage(opp.stage) == null ||
                                    opp.status == 'ON_HOLD' ||
                                    opp.status.startsWith('CLOSED')
                                ? const Text('—')
                                : TextButton(
                                    onPressed: () => onAdvance(opp),
                                    child: const Text('Advance'),
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
