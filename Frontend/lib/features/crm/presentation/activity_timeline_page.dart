import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/auth/crm_rbac.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/activity_service.dart';
import 'widgets/activity_calendar_view.dart';
import 'widgets/log_activity_dialog.dart';

class ActivityTimelinePage extends StatefulWidget {
  const ActivityTimelinePage({
    super.key,
    this.entityType,
    this.entityId,
    this.embedded = false,
  });

  final String? entityType;
  final String? entityId;
  final bool embedded;

  @override
  State<ActivityTimelinePage> createState() => _ActivityTimelinePageState();
}

class _ActivityTimelinePageState extends State<ActivityTimelinePage>
    with SingleTickerProviderStateMixin {
  final _service = ActivityService();
  bool _loading = true;
  String? _error;
  List<ActivityItem> _items = [];
  late final TabController _tabs;
  static const _views = ['my', 'overdue', 'upcoming'];

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 4, vsync: this);
    _tabs.addListener(() {
      if (!_tabs.indexIsChanging && widget.entityType == null) {
        if (_tabs.index < _views.length) {
          _load();
        } else {
          setState(() {});
        }
      }
    });
    if (widget.entityType != null && widget.entityId != null) {
      _load();
    } else {
      _load();
    }
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  String get _currentView =>
      _tabs.index < _views.length ? _views[_tabs.index] : 'my';

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final List<ActivityItem> items;
      if (widget.entityType != null && widget.entityId != null) {
        items = await _service.timeline(
          entityType: widget.entityType!,
          entityId: widget.entityId!,
        );
      } else {
        items = await _service.list(view: _currentView);
      }
      if (!mounted) return;
      setState(() { _items = items; _loading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  Future<void> _openCreate() async {
    if (widget.entityType == null || widget.entityId == null) return;
    final ok = await LogActivityDialog.show(
      context,
      entityType: widget.entityType!,
      entityId: widget.entityId!,
    );
    if (ok != true || !mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Activity logged')),
    );
    await _load();
  }

  Widget _buildBody() {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (widget.entityType == null && _error != null) {
      return Center(child: Text(_error!));
    }
    if (widget.entityType != null && _error != null) return Center(child: Text(_error!));
    if (_items.isEmpty) {
      return const Center(child: Text('No activities yet'));
    }
    return ListView.separated(
      padding: const EdgeInsets.all(CrmSpacing.page),
      itemCount: _items.length,
      separatorBuilder: (_, __) => const Divider(),
      itemBuilder: (_, i) {
        final a = _items[i];
        return ListTile(
          leading: const Icon(Icons.timeline_outlined),
          title: Text(a.subject),
          subtitle: Text(
            '${a.activityTypeCode} · ${a.entityType}'
            '${a.dueOn != null ? ' · due ${a.dueOn!.toLocal()}' : ''}'
            '\n${a.createdOn.toLocal()}'
            '${a.description != null ? '\n${a.description}' : ''}',
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.watch<AuthController>().profile;
    final canCreate = CrmRbac.canCreateActivity(profile);
    final isEntityView = widget.entityType != null;

    if (widget.embedded) {
      return Stack(
        children: [
          RefreshIndicator(onRefresh: _load, child: _buildBody()),
          if (canCreate && isEntityView)
            Positioned(
              right: CrmSpacing.md,
              bottom: CrmSpacing.md,
              child: FloatingActionButton(
                onPressed: _openCreate,
                tooltip: 'Log activity',
                child: const Icon(Icons.add),
              ),
            ),
        ],
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(isEntityView ? 'Activity Timeline' : 'My Activities'),
        actions: !isEntityView && CrmRbac.isManager(profile?['role_code'] as String?)
            ? [
                TextButton(
                  onPressed: () => context.push(CrmRoutes.activityTypes),
                  child: const Text('Types'),
                ),
                TextButton(
                  onPressed: () => context.push(CrmRoutes.activityOutcomes),
                  child: const Text('Outcomes'),
                ),
              ]
            : null,
        bottom: isEntityView
            ? null
            : TabBar(
                controller: _tabs,
                isScrollable: true,
                tabs: const [
                  Tab(text: 'My'),
                  Tab(text: 'Overdue'),
                  Tab(text: 'Upcoming'),
                  Tab(text: 'Calendar'),
                ],
              ),
      ),
      floatingActionButton: canCreate && isEntityView
          ? FloatingActionButton(
              onPressed: _openCreate,
              child: const Icon(Icons.add),
            )
          : null,
      body: isEntityView
          ? RefreshIndicator(onRefresh: _load, child: _buildBody())
          : _tabs.index == 3
              ? const ActivityCalendarView()
              : RefreshIndicator(onRefresh: _load, child: _buildBody()),
    );
  }
}
