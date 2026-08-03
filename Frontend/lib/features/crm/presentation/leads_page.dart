import 'package:flutter/material.dart';

import '../data/lead_model.dart';
import 'lead_form_dialog.dart';
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
    final created = await showLeadFormDialog(context, _controller);
    if (created == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Lead created')),
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
                      hintText: 'Search name, company, email, number',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: IconButton(
                        tooltip: 'Search',
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
                    label: const Text('Add New Lead'),
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
              Text(
                '${_controller.total} lead(s)',
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
                    : _LeadsTable(
                        items: _controller.items,
                        formatValue: _formatInr,
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

class _LeadsTable extends StatelessWidget {
  const _LeadsTable({
    required this.items,
    required this.formatValue,
    required this.onRefresh,
  });

  final List<Lead> items;
  final String Function(double) formatValue;
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
                  ],
                  rows: [
                    for (final lead in items)
                      DataRow(
                        cells: [
                          DataCell(Text(lead.leadNumber)),
                          DataCell(Text(lead.fullName)),
                          DataCell(Text(lead.companyName ?? '—')),
                          DataCell(Text(lead.email ?? '—')),
                          DataCell(Text(lead.phone ?? '—')),
                          DataCell(_StatusChip(status: lead.status)),
                          DataCell(Text(formatValue(lead.estimatedValue))),
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

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.status});

  final String status;

  @override
  Widget build(BuildContext context) {
    return Chip(
      label: Text(status.replaceAll('_', ' ')),
      visualDensity: VisualDensity.compact,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }
}
