import 'package:flutter/material.dart';

import '../../../../core/theme/crm_theme.dart';
import '../../data/activity_service.dart';
import '../../data/lookup_service.dart';

class LogActivityDialog extends StatefulWidget {
  const LogActivityDialog({
    super.key,
    required this.entityType,
    required this.entityId,
    this.lookupService,
    this.activityService,
    this.activityTypes,
    this.outcomesByType,
  });

  final String entityType;
  final String entityId;
  final LookupService? lookupService;
  final ActivityService? activityService;
  final List<String>? activityTypes;
  final Map<String, List<ActivityOutcome>>? outcomesByType;

  static Future<bool?> show(
    BuildContext context, {
    required String entityType,
    required String entityId,
  }) {
    return showDialog<bool>(
      context: context,
      builder: (_) => LogActivityDialog(
        entityType: entityType,
        entityId: entityId,
      ),
    );
  }

  @override
  State<LogActivityDialog> createState() => _LogActivityDialogState();
}

class _LogActivityDialogState extends State<LogActivityDialog> {
  final _subjectCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  final _lookup = LookupService();
  final _activity = ActivityService();
  List<String> _types = CrmLookups.defaults.activityTypes;
  String _selectedType = 'NOTE';
  List<ActivityOutcome> _outcomes = [];
  String? _selectedOutcome;
  bool _loadingTypes = true;
  bool _loadingOutcomes = false;
  bool _saving = false;
  DateTime? _dueDate;

  bool get _requiresOutcome =>
      outcomeRequiredTypes.contains(_selectedType) && _dueDate == null;

  @override
  void initState() {
    super.initState();
    if (widget.activityTypes != null) {
      _types = widget.activityTypes!;
      _selectedType = _types.first;
      _loadingTypes = false;
      _applyPresetOutcomes();
    } else {
      _loadTypes();
    }
  }

  @override
  void dispose() {
    _subjectCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  void _applyPresetOutcomes() {
    final preset = widget.outcomesByType?[_selectedType];
    if (preset != null) {
      _outcomes = preset;
      _selectedOutcome = preset.isNotEmpty ? preset.first.code : null;
    }
  }

  Future<void> _loadTypes() async {
    try {
      final types = await (widget.lookupService ?? _lookup).activityTypes();
      if (!mounted) return;
      setState(() {
        _types = types;
        _selectedType = types.contains(_selectedType) ? _selectedType : types.first;
        _loadingTypes = false;
      });
      await _loadOutcomes();
    } catch (_) {
      if (!mounted) return;
      setState(() => _loadingTypes = false);
    }
  }

  Future<void> _loadOutcomes() async {
    if (!outcomeRequiredTypes.contains(_selectedType)) {
      setState(() {
        _outcomes = [];
        _selectedOutcome = null;
      });
      return;
    }
    final preset = widget.outcomesByType?[_selectedType];
    if (preset != null) {
      setState(() {
        _outcomes = preset;
        _selectedOutcome = preset.isNotEmpty ? preset.first.code : null;
      });
      return;
    }
    setState(() => _loadingOutcomes = true);
    try {
      final outcomes = await (widget.lookupService ?? _lookup)
          .listActivityOutcomes(activityTypeCode: _selectedType);
      if (!mounted) return;
      setState(() {
        _outcomes = outcomes;
        _selectedOutcome = outcomes.isNotEmpty ? outcomes.first.code : null;
        _loadingOutcomes = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _loadingOutcomes = false);
    }
  }

  Future<void> _pickDueDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _dueDate ?? DateTime.now(),
      firstDate: DateTime.now().subtract(const Duration(days: 1)),
      lastDate: DateTime.now().add(const Duration(days: 365 * 2)),
    );
    if (picked != null) {
      setState(() => _dueDate = picked);
    }
  }

  Future<void> _save() async {
    if (_subjectCtrl.text.trim().isEmpty) return;
    if (_requiresOutcome && _selectedOutcome == null) return;
    setState(() => _saving = true);
    try {
      final dueOn = _dueDate == null
          ? null
          : DateTime(_dueDate!.year, _dueDate!.month, _dueDate!.day, 9);
      await (widget.activityService ?? _activity).create(ActivityCreatePayload(
        entityType: widget.entityType,
        entityId: widget.entityId,
        subject: _subjectCtrl.text.trim(),
        description: _descCtrl.text.trim().isEmpty ? null : _descCtrl.text.trim(),
        activityTypeCode: _selectedType,
        outcomeCode: _requiresOutcome ? _selectedOutcome : null,
        dueOn: dueOn,
        status: dueOn != null ? 'PLANNED' : null,
      ));
      if (!mounted) return;
      Navigator.pop(context, true);
    } catch (e) {
      if (!mounted) return;
      setState(() => _saving = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Log activity'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (_loadingTypes)
              const Padding(
                padding: EdgeInsets.all(CrmSpacing.md),
                child: CircularProgressIndicator(),
              )
            else
              DropdownButtonFormField<String>(
                value: _selectedType,
                decoration: const InputDecoration(labelText: 'Activity type'),
                items: _types
                    .map((t) => DropdownMenuItem(
                          value: t,
                          child: Text(t.replaceAll('_', ' ')),
                        ))
                    .toList(),
                onChanged: _saving
                    ? null
                    : (v) async {
                        if (v == null) return;
                        setState(() => _selectedType = v);
                        await _loadOutcomes();
                      },
              ),
            if (_requiresOutcome) ...[
              const SizedBox(height: CrmSpacing.sm),
              if (_loadingOutcomes)
                const Padding(
                  padding: EdgeInsets.all(CrmSpacing.md),
                  child: CircularProgressIndicator(),
                )
              else
                DropdownButtonFormField<String>(
                  value: _selectedOutcome,
                  decoration: const InputDecoration(labelText: 'Outcome *'),
                  items: _outcomes
                      .map((o) => DropdownMenuItem(
                            value: o.code,
                            child: Text(o.name),
                          ))
                      .toList(),
                  onChanged: _saving
                      ? null
                      : (v) => setState(() => _selectedOutcome = v),
                ),
            ],
            const SizedBox(height: CrmSpacing.sm),
            TextField(
              controller: _subjectCtrl,
              decoration: const InputDecoration(labelText: 'Subject *'),
              enabled: !_saving,
            ),
            const SizedBox(height: CrmSpacing.sm),
            TextField(
              controller: _descCtrl,
              decoration: const InputDecoration(labelText: 'Description'),
              maxLines: 3,
              enabled: !_saving,
            ),
            const SizedBox(height: CrmSpacing.sm),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _saving ? null : _pickDueDate,
                    icon: const Icon(Icons.event_outlined, size: 18),
                    label: Text(
                      _dueDate == null
                          ? 'Due date (optional)'
                          : 'Due: ${_dueDate!.year}-${_dueDate!.month.toString().padLeft(2, '0')}-${_dueDate!.day.toString().padLeft(2, '0')}',
                    ),
                  ),
                ),
                if (_dueDate != null)
                  IconButton(
                    tooltip: 'Clear due date',
                    onPressed: _saving
                        ? null
                        : () => setState(() {
                              _dueDate = null;
                              _loadOutcomes();
                            }),
                    icon: const Icon(Icons.clear),
                  ),
              ],
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _saving ? null : () => Navigator.pop(context, false),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: _saving
              ? null
              : () {
                  if (_subjectCtrl.text.trim().isEmpty) return;
                  if (_requiresOutcome && _selectedOutcome == null) return;
                  _save();
                },
          child: _saving
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Save'),
        ),
      ],
    );
  }
}
