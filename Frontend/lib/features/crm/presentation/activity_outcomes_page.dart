import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/auth/crm_rbac.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/lookup_service.dart';

class ActivityOutcomesPage extends StatefulWidget {
  const ActivityOutcomesPage({super.key});

  @override
  State<ActivityOutcomesPage> createState() => _ActivityOutcomesPageState();
}

class _ActivityOutcomesPageState extends State<ActivityOutcomesPage> {
  final _service = LookupService();
  bool _loading = true;
  String? _error;
  String? _typeFilter;
  List<String> _types = [];
  List<ActivityOutcome> _outcomes = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final types = await _service.activityTypes();
      final items = await _service.listActivityOutcomes(
        activityTypeCode: _typeFilter,
        includeInactive: true,
      );
      if (!mounted) return;
      setState(() {
        _types = types;
        _outcomes = items;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  Future<void> _toggle(ActivityOutcome outcome, bool active) async {
    try {
      await _service.updateActivityOutcome(
        outcome.activityOutcomeId,
        isActive: active,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${outcome.code} ${active ? 'activated' : 'deactivated'}')),
      );
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _addOutcome() async {
    final typeCtrl = TextEditingController(text: _typeFilter ?? 'CALL');
    final codeCtrl = TextEditingController();
    final nameCtrl = TextEditingController();
    var isPositive = false;
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setLocal) => AlertDialog(
          title: const Text('Add activity outcome'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: _types.contains(typeCtrl.text)
                      ? typeCtrl.text
                      : (_types.isNotEmpty ? _types.first : 'CALL'),
                  decoration: const InputDecoration(labelText: 'Activity type'),
                  items: _types
                      .map((t) => DropdownMenuItem(value: t, child: Text(t)))
                      .toList(),
                  onChanged: (v) {
                    if (v != null) typeCtrl.text = v;
                    setLocal(() {});
                  },
                ),
                TextField(
                  controller: codeCtrl,
                  decoration: const InputDecoration(labelText: 'Code *'),
                ),
                TextField(
                  controller: nameCtrl,
                  decoration: const InputDecoration(labelText: 'Name *'),
                ),
                CheckboxListTile(
                  value: isPositive,
                  onChanged: (v) => setLocal(() => isPositive = v ?? false),
                  title: const Text('Positive outcome'),
                  contentPadding: EdgeInsets.zero,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
            FilledButton(
              onPressed: () {
                if (codeCtrl.text.trim().isEmpty || nameCtrl.text.trim().isEmpty) return;
                Navigator.pop(ctx, true);
              },
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );
    if (ok != true) {
      typeCtrl.dispose();
      codeCtrl.dispose();
      nameCtrl.dispose();
      return;
    }
    try {
      await _service.createActivityOutcome(
        activityTypeCode: typeCtrl.text,
        code: codeCtrl.text.trim(),
        name: nameCtrl.text.trim(),
        isPositive: isPositive,
      );
      typeCtrl.dispose();
      codeCtrl.dispose();
      nameCtrl.dispose();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Outcome created')),
      );
      await _load();
    } catch (e) {
      typeCtrl.dispose();
      codeCtrl.dispose();
      nameCtrl.dispose();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.watch<AuthController>().profile;
    final canEdit = CrmRbac.isManager(profile?['role_code'] as String?);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Activity outcomes'),
        actions: [
          TextButton(
            onPressed: () => context.push(CrmRoutes.activityTypes),
            child: const Text('Types'),
          ),
        ],
      ),
      floatingActionButton: canEdit
          ? FloatingActionButton(
              onPressed: _addOutcome,
              child: const Icon(Icons.add),
            )
          : null,
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(
                        CrmSpacing.page,
                        CrmSpacing.sm,
                        CrmSpacing.page,
                        0,
                      ),
                      child: DropdownButtonFormField<String?>(
                        value: _typeFilter,
                        decoration: const InputDecoration(
                          labelText: 'Filter by activity type',
                          isDense: true,
                        ),
                        items: [
                          const DropdownMenuItem(value: null, child: Text('All types')),
                          ..._types.map(
                            (t) => DropdownMenuItem(value: t, child: Text(t)),
                          ),
                        ],
                        onChanged: (v) {
                          setState(() => _typeFilter = v);
                          _load();
                        },
                      ),
                    ),
                    Expanded(
                      child: RefreshIndicator(
                        onRefresh: _load,
                        child: ListView.separated(
                          padding: const EdgeInsets.all(CrmSpacing.page),
                          itemCount: _outcomes.length,
                          separatorBuilder: (_, __) => const Divider(),
                          itemBuilder: (_, i) {
                            final o = _outcomes[i];
                            return ListTile(
                              title: Text(o.name),
                              subtitle: Text(
                                '${o.activityTypeCode} · ${o.code}${o.isPositive ? ' · positive' : ''}',
                              ),
                              trailing: Switch(
                                value: o.isActive,
                                onChanged: canEdit ? (v) => _toggle(o, v) : null,
                              ),
                            );
                          },
                        ),
                      ),
                    ),
                  ],
                ),
    );
  }
}
