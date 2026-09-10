import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/edition/edition_controller.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_section_card.dart';
import 'l2c_demo_controller.dart';

class L2cDemoJourneyPage extends StatefulWidget {
  const L2cDemoJourneyPage({super.key, this.controller});

  final L2cDemoController? controller;

  @override
  State<L2cDemoJourneyPage> createState() => _L2cDemoJourneyPageState();
}

class _L2cDemoJourneyPageState extends State<L2cDemoJourneyPage> {
  L2cDemoController? _controller;

  L2cDemoController get controller => _controller!;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_controller != null) return;
    final edition = context.read<EditionController>();
    _controller = widget.controller ??
        L2cDemoController(
          hasOpportunityEdition: edition.hasOpportunity,
          hasSalQuote: edition.hasSalQuote,
        );
    if (widget.controller == null) {
      final tenantCode =
          context.read<AuthController>().profile?['tenant_code'] as String?;
      if (tenantCode != null) {
        _controller!.loadSession(tenantCode);
      }
    }
  }

  @override
  void dispose() {
    if (widget.controller == null) {
      _controller?.dispose();
    }
    super.dispose();
  }

  void _goToStep(BuildContext context, int index) {
    final hasOpp = controller.hasOpportunityEdition;
    switch (index) {
      case 0:
        context.push(CrmRoutes.leadsNew);
      case 1:
      case 2:
        final id = controller.leadId;
        if (id == null) {
          _showNeedId(context, 'Lead ID');
          return;
        }
        context.push(CrmRoutes.leadDetail(id));
      case 3:
        if (hasOpp) {
          final id = controller.opportunityId;
          if (id == null) {
            _showNeedId(context, 'Opportunity ID');
            return;
          }
          context.push(CrmRoutes.opportunityDetail(id));
        } else {
          final id = controller.customerId;
          if (id == null) {
            _showNeedId(context, 'Customer ID');
            return;
          }
          context.push(CrmRoutes.customerDetail(id));
        }
      case 4:
        if (hasOpp) {
          final id = controller.opportunityId;
          if (id == null) {
            _showNeedId(context, 'Opportunity ID');
            return;
          }
          context.push(CrmRoutes.opportunityDetail(id));
        } else {
          final id = controller.customerId;
          if (id == null) {
            _showNeedId(context, 'Customer ID');
            return;
          }
          context.push(CrmRoutes.customerDetail(id));
        }
      case 5:
        final id = controller.customerId;
        if (id == null) {
          _showNeedId(context, 'Customer ID');
          return;
        }
        context.push(CrmRoutes.customerDetail(id));
      case 6:
      case 7:
        if (controller.quotationId != null) {
          context.push(CrmRoutes.quotationDetail(controller.quotationId!));
        } else {
          context.push(CrmRoutes.quotations);
        }
      case 8:
        if (controller.salesOrderId != null) {
          context.push(CrmRoutes.salesOrderDetail(controller.salesOrderId!));
        } else {
          context.push(CrmRoutes.salesOrders);
        }
    }
  }

  void _showNeedId(BuildContext context, String label) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Set $label below or tap Sync IDs')),
    );
  }

  Future<void> _copyUatReport() async {
    final profile = context.read<AuthController>().profile;
    final report = controller.buildUatReport(
      tenantCode: profile?['tenant_code'] as String?,
      tenantName: profile?['tenant_name'] as String?,
      testerName: profile?['display_name'] as String?,
    );
    await Clipboard.setData(ClipboardData(text: report));
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('UAT report copied to clipboard')),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_controller == null) {
      return const SizedBox.shrink();
    }
    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        final steps = controller.steps;
        final isCommunity = !controller.hasOpportunityEdition;
        return ListView(
          padding: const EdgeInsets.all(CrmSpacing.lg),
          children: [
            Text(
              'L2C Demo Journey',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: CrmSpacing.xs),
            Text(
              isCommunity
                  ? 'Community edition UAT — lead converts to customer only '
                      '(no opportunity pipeline). SAL/FIN out of scope.'
                  : controller.hasSalQuote
                      ? 'Professional edition UAT (TC-L2C-CRM-01) including SAL '
                          'quotation convert and sales-order confirm.'
                      : 'Professional edition UAT (TC-L2C-CRM-01). SAL quotation '
                          'and FIN payment are out of scope until governance sign-off.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: CrmSpacing.md),
            LinearProgressIndicator(value: controller.progress),
            const SizedBox(height: CrmSpacing.xs),
            Text(
              '${controller.completedCount} of ${steps.length} steps marked complete',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: CrmSpacing.md),
            Wrap(
              spacing: CrmSpacing.sm,
              runSpacing: CrmSpacing.sm,
              children: [
                FilledButton.icon(
                  onPressed: controller.syncing
                      ? null
                      : () => controller.detectProgress(),
                  icon: controller.syncing
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.fact_check_outlined, size: 18),
                  label: const Text('Check progress'),
                ),
                OutlinedButton.icon(
                  onPressed: controller.syncing
                      ? null
                      : () => controller.syncLatest(),
                  icon: const Icon(Icons.sync, size: 18),
                  label: const Text('Sync IDs'),
                ),
                OutlinedButton.icon(
                  onPressed: _copyUatReport,
                  icon: const Icon(Icons.copy_outlined, size: 18),
                  label: const Text('Copy UAT report'),
                ),
                TextButton(
                  onPressed: () => controller.reset(),
                  child: const Text('Reset'),
                ),
              ],
            ),
            if (controller.error != null) ...[
              const SizedBox(height: CrmSpacing.sm),
              Text(
                controller.error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ],
            const SizedBox(height: CrmSpacing.md),
            CrmSectionCard(
              title: 'Demo record IDs',
              child: Column(
                children: [
                  _IdField(
                    label: 'Lead ID',
                    value: controller.leadId,
                    onChanged: controller.setLeadId,
                  ),
                  if (!isCommunity)
                    _IdField(
                      label: 'Opportunity ID',
                      value: controller.opportunityId,
                      onChanged: controller.setOpportunityId,
                    ),
                  _IdField(
                    label: 'Customer ID',
                    value: controller.customerId,
                    onChanged: controller.setCustomerId,
                  ),
                  if (!isCommunity && controller.hasSalQuote) ...[
                    _IdField(
                      label: 'Quotation ID',
                      value: controller.quotationId,
                      onChanged: controller.setQuotationId,
                    ),
                    _IdField(
                      label: 'Sales order ID',
                      value: controller.salesOrderId,
                      onChanged: controller.setSalesOrderId,
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: CrmSpacing.md),
            for (var i = 0; i < steps.length; i++)
              _StepCard(
                index: i,
                title: steps[i].$1,
                description: steps[i].$2,
                hint: steps[i].$3,
                done: controller.completedSteps.contains(i),
                onToggle: () => controller.toggleStep(i),
                onGo: () => _goToStep(context, i),
              ),
          ],
        );
      },
    );
  }
}

class _IdField extends StatefulWidget {
  const _IdField({
    required this.label,
    required this.value,
    required this.onChanged,
  });

  final String label;
  final String? value;
  final ValueChanged<String?> onChanged;

  @override
  State<_IdField> createState() => _IdFieldState();
}

class _IdFieldState extends State<_IdField> {
  late final TextEditingController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = TextEditingController(text: widget.value ?? '');
  }

  @override
  void didUpdateWidget(covariant _IdField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != oldWidget.value && widget.value != _ctrl.text) {
      _ctrl.text = widget.value ?? '';
    }
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: CrmSpacing.sm),
      child: TextField(
        controller: _ctrl,
        decoration: InputDecoration(
          labelText: widget.label,
          hintText: 'Paste UUID from list/detail',
          isDense: true,
        ),
        onChanged: widget.onChanged,
      ),
    );
  }
}

class _StepCard extends StatelessWidget {
  const _StepCard({
    required this.index,
    required this.title,
    required this.description,
    required this.hint,
    required this.done,
    required this.onToggle,
    required this.onGo,
  });

  final int index;
  final String title;
  final String description;
  final String hint;
  final bool done;
  final VoidCallback onToggle;
  final VoidCallback onGo;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: CrmSpacing.sm),
      child: Padding(
        padding: const EdgeInsets.all(CrmSpacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 14,
                  backgroundColor: done
                      ? Theme.of(context).colorScheme.primary
                      : Theme.of(context).colorScheme.surfaceContainerHighest,
                  child: Text(
                    '${index + 1}',
                    style: TextStyle(
                      fontSize: 12,
                      color: done
                          ? Theme.of(context).colorScheme.onPrimary
                          : Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
                const SizedBox(width: CrmSpacing.sm),
                Expanded(
                  child: Text(title, style: Theme.of(context).textTheme.titleSmall),
                ),
                Checkbox(value: done, onChanged: (_) => onToggle()),
              ],
            ),
            const SizedBox(height: CrmSpacing.xs),
            Text(description),
            const SizedBox(height: CrmSpacing.xs),
            Text(
              hint,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: CrmSpacing.sm),
            Align(
              alignment: Alignment.centerRight,
              child: FilledButton.tonal(
                onPressed: onGo,
                child: const Text('Go to step'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
