import 'package:flutter/material.dart';
import 'package:customertracker/features/platform/data/branding_service.dart';

class BrandingPrimaryColorScreen extends StatefulWidget {
  const BrandingPrimaryColorScreen({super.key});

  @override
  State<BrandingPrimaryColorScreen> createState() =>
      _BrandingPrimaryColorScreenState();
}

class _BrandingPrimaryColorScreenState
    extends State<BrandingPrimaryColorScreen> {
  String? _currentColor;
  bool _loading = false;
  final _service = BrandingService();

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final b = await _service.getBranding();
      setState(() => _currentColor = b.primaryColor ?? '#1565C0');
    } catch (_) {
      setState(() => _currentColor = '#1565C0');
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _pickAndSave() async {
    // Simple preset picker for quick change
    final presets = ['#1565C0', '#0D47A1', '#2E7D32', '#C62828', '#FF8F00'];
    final picked = await showDialog<String?>(
      context: context,
      builder: (_) => SimpleDialog(
        title: const Text('Select primary color'),
        children: presets
            .map((c) => SimpleDialogOption(
                  child: Row(children: [
                    Container(
                      width: 24,
                      height: 24,
                      color: Color(int.parse('0xFF${c.substring(1)}')),
                    ),
                    const SizedBox(width: 8),
                    Text(c)
                  ]),
                  onPressed: () => Navigator.pop(context, c),
                ))
            .toList(),
      ),
    );
    if (picked == null) return;
    setState(() => _loading = true);
    try {
      final resp = await _service.updatePrimaryColor(picked);
      setState(() => _currentColor = resp.primaryColor);
    } catch (e) {
      if (!mounted) return;
      await showDialog<void>(
          context: context,
          builder: (_) => AlertDialog(
                  title: const Text('Error'),
                  content: Text(e.toString()),
                  actions: [
                    TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text('OK'))
                  ]));
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final accent = _currentColor ?? '#1565C0';
    final accentColor = Color(int.parse('0xFF${accent.substring(1)}'));
    return Scaffold(
      appBar: AppBar(title: const Text('Branding - Primary Color')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Current primary color: $accent'),
            const SizedBox(height: 12),
            Container(height: 48, color: accentColor),
            const SizedBox(height: 24),
            ElevatedButton.icon(
                onPressed: _loading ? null : _pickAndSave,
                icon: const Icon(Icons.palette),
                label: Text(_loading ? 'Saving...' : 'Change Primary Color')),
            const SizedBox(height: 32),
            const Text('PDF Accent Preview'),
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(height: 8, color: accentColor),
                      const SizedBox(height: 12),
                      Text('Invoice Preview',
                          style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 8),
                      Text('Company Name',
                          style: TextStyle(
                              color: accentColor, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      Text('Invoice # INV-2026-0001'),
                    ]),
              ),
            )
          ],
        ),
      ),
    );
  }
}
