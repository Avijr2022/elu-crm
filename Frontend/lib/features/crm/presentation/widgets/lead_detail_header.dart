import 'package:flutter/material.dart';

import '../../../../core/theme/crm_theme.dart';
import '../../../../core/widgets/crm_status_chip.dart';
import '../../data/lead_model.dart';

class LeadDetailHeader extends StatelessWidget {
  const LeadDetailHeader({super.key, required this.lead});

  final Lead lead;

  String get _initials {
    final parts = lead.fullName.trim().split(RegExp(r'\s+'));
    if (parts.isEmpty) return '?';
    if (parts.length == 1) {
      return parts.first.substring(0, 1).toUpperCase();
    }
    return '${parts.first[0]}${parts.last[0]}'.toUpperCase();
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
          CircleAvatar(
            radius: 40,
            backgroundColor: scheme.primaryContainer,
            child: Text(
              _initials,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: scheme.onPrimaryContainer,
                  ),
            ),
          ),
          const SizedBox(height: CrmSpacing.sm),
          Text(
            lead.fullName,
            style: Theme.of(context).textTheme.headlineSmall,
            textAlign: TextAlign.center,
          ),
          if (lead.companyName != null && lead.companyName!.isNotEmpty) ...[
            const SizedBox(height: CrmSpacing.xs),
            Text(
              lead.companyName!,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: scheme.onSurfaceVariant,
                  ),
              textAlign: TextAlign.center,
            ),
          ],
          const SizedBox(height: CrmSpacing.xs),
          Text(
            lead.leadNumber,
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: CrmSpacing.sm),
          CrmStatusChip(status: lead.status),
          const SizedBox(height: CrmSpacing.md),
          Wrap(
            alignment: WrapAlignment.center,
            spacing: CrmSpacing.sm,
            children: [
              _QuickAction(
                icon: Icons.call_outlined,
                tooltip: 'Call',
                enabled: lead.phone != null && lead.phone!.isNotEmpty,
              ),
              _QuickAction(
                icon: Icons.mail_outlined,
                tooltip: 'Email',
                enabled: lead.email != null && lead.email!.isNotEmpty,
              ),
              const _QuickAction(
                icon: Icons.event_outlined,
                tooltip: 'Follow-up (coming soon)',
                enabled: false,
              ),
              const _QuickAction(
                icon: Icons.attach_file_outlined,
                tooltip: 'Attachments (coming soon)',
                enabled: false,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _QuickAction extends StatelessWidget {
  const _QuickAction({
    required this.icon,
    required this.tooltip,
    required this.enabled,
  });

  final IconData icon;
  final String tooltip;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    return IconButton.filledTonal(
      onPressed: enabled ? () {} : null,
      tooltip: tooltip,
      icon: Icon(icon),
    );
  }
}
