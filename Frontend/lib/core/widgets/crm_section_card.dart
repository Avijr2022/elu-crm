import 'package:flutter/material.dart';

import '../theme/crm_theme.dart';

class CrmSectionCard extends StatelessWidget {
  const CrmSectionCard({
    super.key,
    this.title,
    required this.child,
    this.onTap,
    this.trailing,
  });

  final String? title;
  final Widget child;
  final VoidCallback? onTap;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    final content = Padding(
      padding: const EdgeInsets.all(CrmSpacing.md),
      child: child,
    );

    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(CrmRadii.section),
      ),
      clipBehavior: Clip.antiAlias,
      child: onTap == null
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                if (title != null) _Header(title: title!, trailing: trailing),
                content,
              ],
            )
          : InkWell(
              onTap: onTap,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (title != null) _Header(title: title!, trailing: trailing),
                  content,
                ],
              ),
            ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.title, this.trailing});

  final String title;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        CrmSpacing.md,
        CrmSpacing.sm,
        CrmSpacing.sm,
        0,
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(title, style: Theme.of(context).textTheme.titleSmall),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}
