import 'package:flutter/material.dart';

import '../../../../core/theme/crm_theme.dart';
import '../../data/activity_service.dart';

class ActivityCalendarView extends StatefulWidget {
  const ActivityCalendarView({super.key});

  @override
  State<ActivityCalendarView> createState() => _ActivityCalendarViewState();
}

class _ActivityCalendarViewState extends State<ActivityCalendarView> {
  final _service = ActivityService();
  DateTime _month = DateTime(DateTime.now().year, DateTime.now().month);
  bool _loading = true;
  String? _error;
  Map<DateTime, List<ActivityItem>> _byDay = {};

  @override
  void initState() {
    super.initState();
    _load();
  }

  DateTime _dateKey(DateTime dt) => DateTime(dt.year, dt.month, dt.day);

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final items = [
        ...await _service.list(view: 'my'),
        ...await _service.list(view: 'upcoming'),
      ];
      final map = <DateTime, List<ActivityItem>>{};
      for (final a in items) {
        final due = a.dueOn ?? a.createdOn;
        final key = _dateKey(due.toLocal());
        map.putIfAbsent(key, () => []).add(a);
      }
      if (!mounted) return;
      setState(() { _byDay = map; _loading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  void _shiftMonth(int delta) {
    setState(() {
      _month = DateTime(_month.year, _month.month + delta);
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
            TextButton(onPressed: _load, child: const Text('Retry')),
          ],
        ),
      );
    }

    final first = DateTime(_month.year, _month.month, 1);
    final daysInMonth = DateTime(_month.year, _month.month + 1, 0).day;
    final startWeekday = first.weekday % 7;
    final monthLabel =
        '${_month.year}-${_month.month.toString().padLeft(2, '0')}';

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: CrmSpacing.page),
          child: Row(
            children: [
              IconButton(onPressed: () => _shiftMonth(-1), icon: const Icon(Icons.chevron_left)),
              Expanded(
                child: Text(monthLabel, textAlign: TextAlign.center, style: Theme.of(context).textTheme.titleMedium),
              ),
              IconButton(onPressed: () => _shiftMonth(1), icon: const Icon(Icons.chevron_right)),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: CrmSpacing.page),
          child: Row(
            children: ['S', 'M', 'T', 'W', 'T', 'F', 'S']
                .map((d) => Expanded(
                      child: Center(
                        child: Text(d, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12)),
                      ),
                    ))
                .toList(),
          ),
        ),
        Expanded(
          child: GridView.builder(
            padding: const EdgeInsets.all(CrmSpacing.page),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 7,
              mainAxisSpacing: 4,
              crossAxisSpacing: 4,
            ),
            itemCount: startWeekday + daysInMonth,
            itemBuilder: (_, i) {
              if (i < startWeekday) return const SizedBox.shrink();
              final day = i - startWeekday + 1;
              final date = DateTime(_month.year, _month.month, day);
              final key = _dateKey(date);
              final events = _byDay[key] ?? [];
              final isToday = _dateKey(DateTime.now()) == key;
              return Container(
                decoration: BoxDecoration(
                  border: Border.all(
                    color: isToday
                        ? Theme.of(context).colorScheme.primary
                        : Theme.of(context).colorScheme.outlineVariant,
                  ),
                  borderRadius: BorderRadius.circular(6),
                ),
                padding: const EdgeInsets.all(4),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('$day', style: TextStyle(
                      fontWeight: isToday ? FontWeight.bold : FontWeight.normal,
                      fontSize: 12,
                    )),
                    if (events.isNotEmpty)
                      Expanded(
                        child: ListView(
                          children: events.take(2).map((e) => Text(
                            e.subject,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              fontSize: 9,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                          )).toList(),
                        ),
                      ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
