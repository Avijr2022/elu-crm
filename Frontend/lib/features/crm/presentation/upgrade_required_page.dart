import 'package:flutter/material.dart';

import '../../../core/theme/crm_theme.dart';

class UpgradeRequiredPage extends StatelessWidget {
  const UpgradeRequiredPage({super.key, this.featureCode});

  final String? featureCode;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Upgrade required')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(CrmSpacing.lg),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.lock_outline, size: 48),
              const SizedBox(height: CrmSpacing.sm),
              Text(
                featureCode ?? 'This feature',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: CrmSpacing.xs),
              const Text(
                'Not included in your edition. Upgrade to Professional or Enterprise.',
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
