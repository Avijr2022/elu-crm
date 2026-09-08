import 'package:flutter/material.dart';

import 'lead_form_page.dart';
import 'leads_controller.dart';

/// Navigates to [LeadFormPage] for create. Returns true when saved.
Future<bool?> showLeadFormDialog(
  BuildContext context,
  LeadsController controller,
) {
  return Navigator.push<bool>(
    context,
    MaterialPageRoute(builder: (_) => const LeadFormPage()),
  ).then((saved) async {
    if (saved == true) await controller.load();
    return saved;
  });
}
