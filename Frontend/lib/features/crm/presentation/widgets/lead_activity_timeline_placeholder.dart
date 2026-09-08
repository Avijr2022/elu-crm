import 'package:flutter/material.dart';

import '../../../../core/theme/crm_theme.dart';

/// Placeholder for CRM-004 activity timeline embed. Replace internals in Phase 4.
class LeadActivityTimelinePlaceholder extends StatelessWidget {
  const LeadActivityTimelinePlaceholder({super.key, required this.leadId});

  final String leadId;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(CrmSpacing.lg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.timeline_outlined,
              size: 48,
              color: Theme.of(context).colorScheme.outline,
            ),
            const SizedBox(height: CrmSpacing.sm),
            Text(
              'Activity timeline',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: CrmSpacing.xs),
            Text(
              'Calls, meetings, tasks and notes for this lead will appear here.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}
