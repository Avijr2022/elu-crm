import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/crm_theme.dart';
import '../data/branding_service.dart';

class TenantBrandingPage extends StatefulWidget {
  const TenantBrandingPage({super.key});

  @override
  State<TenantBrandingPage> createState() => _TenantBrandingPageState();
}

class _TenantBrandingPageState extends State<TenantBrandingPage> {
  final _service = BrandingService();
  bool _loading = true;
  bool _uploading = false;
  String? _error;
  String? _logoUrl;
  String? _primaryColor;

  static const _colorPresets = ['#1565C0', '#2E7D32', '#6A1B9A', '#C62828', '#EF6C00'];

  bool get _canUpload {
    final perms = context.read<AuthController>().profile?['permissions'];
    if (perms is List) {
      return perms.contains('tenant.update');
    }
    return false;
  }

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
      final branding = await _service.getBranding();
      if (!mounted) return;
      setState(() {
        _logoUrl = branding.logoUrl;
        _primaryColor = branding.primaryColor ?? '#1565C0';
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

  Future<void> _pickAndUpload() async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['png', 'jpg', 'jpeg'],
      withData: true,
    );
    if (result == null || result.files.isEmpty) return;
    final file = result.files.first;
    final bytes = file.bytes;
    if (bytes == null) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not read selected file')),
      );
      return;
    }
    final ext = (file.extension ?? 'png').toLowerCase();
    final mime = ext == 'png' ? 'png' : 'jpeg';
    final dataUrl = 'data:image/$mime;base64,${base64Encode(bytes)}';

    setState(() => _uploading = true);
    try {
      final branding = await _service.uploadLogo(dataUrl);
      if (!mounted) return;
      setState(() => _logoUrl = branding.logoUrl);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Logo uploaded')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  Color? _parseColor(String? hex) {
    if (hex == null || hex.length != 7 || !hex.startsWith('#')) return null;
    try {
      return Color(int.parse(hex.substring(1), radix: 16) + 0xFF000000);
    } catch (_) {
      return null;
    }
  }

  Future<void> _saveColor(String color) async {
    setState(() => _uploading = true);
    try {
      final branding = await _service.updatePrimaryColor(color);
      if (!mounted) return;
      setState(() => _primaryColor = branding.primaryColor);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Primary color updated')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  Widget _logoPreview() {
    if (_logoUrl == null || _logoUrl!.isEmpty) {
      return const Text('No logo configured');
    }
    final match = RegExp(r'^data:image/(png|jpeg);base64,(.+)$', caseSensitive: false)
        .firstMatch(_logoUrl!);
    if (match == null) return const Text('Logo preview unavailable');
    try {
      final bytes = base64Decode(match.group(2)!);
      return ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: Image.memory(bytes, width: 120, height: 120, fit: BoxFit.contain),
      );
    } catch (_) {
      return const Text('Logo preview unavailable');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tenant branding')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(CrmSpacing.page),
              children: [
                if (_error != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: CrmSpacing.md),
                    child: Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                  ),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(CrmSpacing.md),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Logo', style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: CrmSpacing.md),
                        _logoPreview(),
                        const SizedBox(height: CrmSpacing.md),
                        Text(
                          'Used on quotation PDF exports. PNG or JPEG, max 2 MB.',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        if (_canUpload) ...[
                          const SizedBox(height: CrmSpacing.md),
                          FilledButton.icon(
                            onPressed: _uploading ? null : _pickAndUpload,
                            icon: _uploading
                                ? const SizedBox(
                                    width: 18,
                                    height: 18,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  )
                                : const Icon(Icons.upload_file),
                            label: const Text('Upload logo'),
                          ),
                        ] else
                          Padding(
                            padding: const EdgeInsets.only(top: CrmSpacing.sm),
                            child: Text(
                              'You need tenant.update permission to change the logo.',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: CrmSpacing.sm),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(CrmSpacing.md),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Primary color', style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: CrmSpacing.sm),
                        Container(
                          height: 8,
                          decoration: BoxDecoration(
                            color: _parseColor(_primaryColor) ?? Colors.blue,
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                        const SizedBox(height: CrmSpacing.sm),
                        Text(
                          'PDF quotation header accent bar preview',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        if (_canUpload) ...[
                          const SizedBox(height: CrmSpacing.md),
                          Wrap(
                            spacing: CrmSpacing.sm,
                            children: _colorPresets
                                .map(
                                  (c) => ChoiceChip(
                                    label: Text(c),
                                    selected: _primaryColor == c,
                                    onSelected: _uploading
                                        ? null
                                        : (_) => _saveColor(c),
                                  ),
                                )
                                .toList(),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ],
            ),
    );
  }
}
