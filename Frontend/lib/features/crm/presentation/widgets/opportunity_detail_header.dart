import 'package:flutter/material.dart';

import '../../../../core/theme/crm_theme.dart';
import '../../data/opportunity_model.dart';

class OpportunityDetailHeader extends StatelessWidget {
  const OpportunityDetailHeader({
    super.key,
    required this.opportunity,
    required this.formatValue,
    required this.formatWeighted,
    required this.formatDate,
  });

  final Opportunity opportunity;
  final String Function(Opportunity) formatValue;
  final String Function(Opportunity) formatWeighted;
  final String Function(DateTime?) formatDate;

  Color _stageColor(ColorScheme scheme) {
    switch (opportunity.stage) {
      case 'QUALIFICATION':
      case 'TECHNICAL_EVAL':
        return Colors.blue.shade100;
      case 'BUDGET_VALIDATION':
      case 'PROPOSAL':
      case 'QUOTATION_ISSUED':
        return Colors.amber.shade100;
      case 'NEGOTIATION':
        return Colors.green.shade100;
      default:
        return scheme.surfaceContainerHighest;
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        CrmSpacing.page,
        CrmSpacing.sm,
        CrmSpacing.page,
        CrmSpacing.md,
      ),
      child: Column(
        children: [
          Text(
            opportunity.name,
            style: Theme.of(context).textTheme.headlineSmall,
            textAlign: TextAlign.center,
          ),
          if (opportunity.companyName != null &&
              opportunity.companyName!.isNotEmpty) ...[
            const SizedBox(height: CrmSpacing.xs),
            Text(
              opportunity.companyName!,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: scheme.onSurfaceVariant,
                  ),
              textAlign: TextAlign.center,
            ),
          ],
          const SizedBox(height: CrmSpacing.xs),
          Text(
            opportunity.opportunityNumber,
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: CrmSpacing.sm),
          Chip(
            label: Text(opportunity.stage.replaceAll('_', ' ')),
            backgroundColor: _stageColor(scheme),
            side: BorderSide.none,
            visualDensity: VisualDensity.compact,
          ),
          const SizedBox(height: CrmSpacing.sm),
          Text(
            formatValue(opportunity),
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: CrmSpacing.xs),
          Text(
            'Close: ${formatDate(opportunity.expectedCloseDate)} · '
            '${opportunity.probability}% · '
            'Weighted ${formatWeighted(opportunity)}',
            style: Theme.of(context).textTheme.bodySmall,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
