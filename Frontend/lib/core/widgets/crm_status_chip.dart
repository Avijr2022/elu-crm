import 'package:flutter/material.dart';

class CrmStatusChip extends StatelessWidget {
  const CrmStatusChip({super.key, required this.status});

  final String status;

  Color? _background(ColorScheme scheme) {
    switch (status) {
      case 'NEW':
        return scheme.primaryContainer;
      case 'UNDER_QUALIFICATION':
        return scheme.tertiaryContainer;
      case 'QUALIFIED':
        return scheme.secondaryContainer;
      case 'NURTURE':
        return scheme.surfaceContainerHighest;
      case 'ON_HOLD':
        return scheme.surfaceContainerHigh;
      case 'CONVERTED':
        return Colors.green.shade100;
      case 'DISQUALIFIED':
        return scheme.errorContainer;
      default:
        return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final bg = _background(scheme);
    return Chip(
      label: Text(status.replaceAll('_', ' ')),
      visualDensity: VisualDensity.compact,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      backgroundColor: bg,
      side: bg == null ? null : BorderSide.none,
    );
  }
}
