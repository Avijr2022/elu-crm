import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/auth/crm_rbac.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/lookup_service.dart';

class ActivityTypesPage extends StatefulWidget {
  const ActivityTypesPage({super.key});

  @override
  State<ActivityTypesPage> createState() => _ActivityTypesPageState();
}

class _ActivityTypesPageState extends State<ActivityTypesPage> {
  final _service = LookupService();
  bool _loading = true;
  String? _error;
  List<ActivityType> _types = [];

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
      final items = await _service.listActivityTypes(includeInactive: true);
      if (!mounted) return;
      setState(() {
        _types = items;
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

  Future<void> _addType() async {
    final codeCtrl = TextEditingController();
    final nameCtrl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add activity type'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: codeCtrl,
              decoration: const InputDecoration(
                labelText: 'Code *',
                hintText: 'e.g. VISIT',
              ),
              textCapitalization: TextCapitalization.characters,
            ),
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(labelText: 'Name *'),
            ),
          ],
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
    );
    if (ok != true) {
      codeCtrl.dispose();
      nameCtrl.dispose();
      return;
    }
    try {
      await _service.createActivityType(
        code: codeCtrl.text.trim(),
        name: nameCtrl.text.trim(),
      );
      codeCtrl.dispose();
      nameCtrl.dispose();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Activity type created')),
      );
      await _load();
    } catch (e) {
      codeCtrl.dispose();
      nameCtrl.dispose();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _toggle(ActivityType type, bool active) async {
    try {
      await _service.updateActivityType(type.activityTypeId, isActive: active);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${type.code} ${active ? 'activated' : 'deactivated'}')),
      );
      await _load();
    } catch (e) {
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
        title: const Text('Activity types'),
        actions: [
          TextButton(
            onPressed: () => context.push(CrmRoutes.activityOutcomes),
            child: const Text('Outcomes'),
          ),
        ],
      ),
      floatingActionButton: canEdit
          ? FloatingActionButton(
              onPressed: _addType,
              child: const Icon(Icons.add),
            )
          : null,
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(_error!),
                      TextButton(onPressed: _load, child: const Text('Retry')),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.separated(
                    padding: const EdgeInsets.all(CrmSpacing.page),
                    itemCount: _types.length,
                    separatorBuilder: (_, __) => const Divider(),
                    itemBuilder: (_, i) {
                      final t = _types[i];
                      return ListTile(
                        leading: const Icon(Icons.category_outlined),
                        title: Text(t.name),
                        subtitle: Text(t.code),
                        trailing: Switch(
                          value: t.isActive,
                          onChanged: canEdit ? (v) => _toggle(t, v) : null,
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
