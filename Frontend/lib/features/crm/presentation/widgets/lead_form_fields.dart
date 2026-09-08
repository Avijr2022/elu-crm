import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../core/theme/crm_theme.dart';

class LeadFormData {
  LeadFormData({
    required this.fullName,
    this.companyName,
    this.email,
    this.phone,
    required this.status,
    required this.estimatedValue,
    this.notes,
  });

  final String fullName;
  final String? companyName;
  final String? email;
  final String? phone;
  final String status;
  final double estimatedValue;
  final String? notes;
}

class LeadFormFields extends StatelessWidget {
  const LeadFormFields({
    super.key,
    required this.nameCtrl,
    required this.companyCtrl,
    required this.emailCtrl,
    required this.phoneCtrl,
    required this.valueCtrl,
    required this.notesCtrl,
    required this.status,
    required this.onStatusChanged,
    this.readOnly = false,
    this.enabled = true,
  });

  final TextEditingController nameCtrl;
  final TextEditingController companyCtrl;
  final TextEditingController emailCtrl;
  final TextEditingController phoneCtrl;
  final TextEditingController valueCtrl;
  final TextEditingController notesCtrl;
  final String status;
  final ValueChanged<String> onStatusChanged;
  final bool readOnly;
  final bool enabled;

  static const editableStatuses = [
    'NEW',
    'UNDER_QUALIFICATION',
    'NURTURE',
    'ON_HOLD',
    'QUALIFIED',
  ];

  @override
  Widget build(BuildContext context) {
    final canEdit = enabled && !readOnly;
    final statuses = editableStatuses.contains(status)
        ? editableStatuses
        : [...editableStatuses, status];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextFormField(
          controller: nameCtrl,
          decoration: const InputDecoration(labelText: 'Full Name *'),
          textInputAction: TextInputAction.next,
          readOnly: readOnly,
          enabled: canEdit,
          validator: (v) =>
              (v == null || v.trim().isEmpty) ? 'Required' : null,
        ),
        const SizedBox(height: CrmSpacing.sm),
        TextFormField(
          controller: companyCtrl,
          decoration: const InputDecoration(labelText: 'Company'),
          textInputAction: TextInputAction.next,
          readOnly: readOnly,
          enabled: canEdit,
        ),
        const SizedBox(height: CrmSpacing.sm),
        TextFormField(
          controller: emailCtrl,
          decoration: const InputDecoration(labelText: 'Email'),
          keyboardType: TextInputType.emailAddress,
          textInputAction: TextInputAction.next,
          readOnly: readOnly,
          enabled: canEdit,
        ),
        const SizedBox(height: CrmSpacing.sm),
        TextFormField(
          controller: phoneCtrl,
          decoration: const InputDecoration(labelText: 'Phone'),
          keyboardType: TextInputType.phone,
          textInputAction: TextInputAction.next,
          readOnly: readOnly,
          enabled: canEdit,
        ),
        const SizedBox(height: CrmSpacing.sm),
        DropdownButtonFormField<String>(
          value: status,
          decoration: const InputDecoration(labelText: 'Stage / Status'),
          items: statuses
              .map((s) => DropdownMenuItem(
                    value: s,
                    child: Text(s.replaceAll('_', ' ')),
                  ))
              .toList(),
          onChanged: canEdit ? (v) => onStatusChanged(v ?? status) : null,
        ),
        const SizedBox(height: CrmSpacing.sm),
        TextFormField(
          controller: valueCtrl,
          decoration: const InputDecoration(
            labelText: 'Estimated Value (INR)',
            prefixText: '₹ ',
          ),
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          inputFormatters: [
            FilteringTextInputFormatter.allow(RegExp(r'[0-9.]')),
          ],
          readOnly: readOnly,
          enabled: canEdit,
        ),
        const SizedBox(height: CrmSpacing.sm),
        TextFormField(
          controller: notesCtrl,
          decoration: const InputDecoration(labelText: 'Notes'),
          maxLines: 3,
          readOnly: readOnly,
          enabled: canEdit,
        ),
      ],
    );
  }
}
