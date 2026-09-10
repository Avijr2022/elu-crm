import 'package:flutter/material.dart';

import '../theme/crm_theme.dart';

class CrmSearchField extends StatelessWidget {
  const CrmSearchField({
    super.key,
    required this.controller,
    required this.hintText,
    required this.onSearch,
  });

  final TextEditingController controller;
  final String hintText;
  final VoidCallback onSearch;

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      decoration: crmSearchDecoration(
        hintText: hintText,
        suffixIcon: IconButton(
          tooltip: 'Search',
          onPressed: onSearch,
          icon: const Icon(Icons.arrow_forward),
        ),
      ),
      onSubmitted: (_) => onSearch(),
    );
  }
}
