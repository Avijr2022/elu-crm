import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';
import '../../../core/auth/crm_rbac.dart';
import '../../../core/edition/edition_controller.dart';
import '../../../core/routing/crm_routes.dart';
import '../../../core/theme/crm_theme.dart';
import '../../../core/widgets/crm_section_card.dart';
import '../data/customer_service.dart';
import '../data/opportunity_model.dart';
import '../data/opportunity_service.dart';

class CustomerDetailPage extends StatefulWidget {
  const CustomerDetailPage({super.key, required this.customerId});
  final String customerId;

  @override
  State<CustomerDetailPage> createState() => _CustomerDetailPageState();
}

class _CustomerDetailPageState extends State<CustomerDetailPage> {
  final _service = CustomerService();
  final _oppService = OpportunityService();
  bool _loading = true;
  String? _error;
  Customer? _customer;
  List<Opportunity> _opportunities = [];
  bool _loadingOpps = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final c = await _service.getById(widget.customerId);
      if (!mounted) return;
      setState(() { _customer = c; _loading = false; });
      _loadOpportunities();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  Future<void> _loadOpportunities() async {
    final edition = context.read<EditionController>();
    if (!edition.hasOpportunity) return;
    setState(() => _loadingOpps = true);
    try {
      final result = await _oppService.listForCustomer(widget.customerId);
      if (!mounted) return;
      setState(() {
        _opportunities = result.items;
        _loadingOpps = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _loadingOpps = false);
    }
  }

  Future<void> _addContact() async {
    final first = TextEditingController();
    final last = TextEditingController();
    final email = TextEditingController();
    final phone = TextEditingController();
    var primary = false;
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setLocal) => AlertDialog(
          title: const Text('Add contact'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: first, decoration: const InputDecoration(labelText: 'First name *')),
                TextField(controller: last, decoration: const InputDecoration(labelText: 'Last name')),
                TextField(controller: email, decoration: const InputDecoration(labelText: 'Email')),
                TextField(controller: phone, decoration: const InputDecoration(labelText: 'Mobile')),
                CheckboxListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Primary contact'),
                  value: primary,
                  onChanged: (v) => setLocal(() => primary = v ?? false),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
            FilledButton(
              onPressed: () {
                if (first.text.trim().isEmpty) return;
                Navigator.pop(ctx, true);
              },
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );
    if (ok != true || !mounted) {
      first.dispose(); last.dispose(); email.dispose(); phone.dispose();
      return;
    }
    try {
      await _service.addContact(
        widget.customerId,
        firstName: first.text.trim(),
        lastName: last.text.trim().isEmpty ? null : last.text.trim(),
        email: email.text.trim().isEmpty ? null : email.text.trim(),
        phoneMobile: phone.text.trim().isEmpty ? null : phone.text.trim(),
        isPrimary: primary,
      );
      first.dispose(); last.dispose(); email.dispose(); phone.dispose();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Contact added')));
      await _load();
    } catch (e) {
      first.dispose(); last.dispose(); email.dispose(); phone.dispose();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _addAddress() async {
    final line1 = TextEditingController();
    final city = TextEditingController();
    final state = TextEditingController();
    final country = TextEditingController(text: 'India');
    final postal = TextEditingController();
    var type = 'REGISTERED';
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setLocal) => AlertDialog(
          title: const Text('Add address'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: type,
                  decoration: const InputDecoration(labelText: 'Type'),
                  items: const [
                    DropdownMenuItem(value: 'REGISTERED', child: Text('Registered')),
                    DropdownMenuItem(value: 'BILLING', child: Text('Billing')),
                    DropdownMenuItem(value: 'SHIPPING', child: Text('Shipping')),
                  ],
                  onChanged: (v) => setLocal(() => type = v ?? 'REGISTERED'),
                ),
                TextField(controller: line1, decoration: const InputDecoration(labelText: 'Address line 1 *')),
                TextField(controller: city, decoration: const InputDecoration(labelText: 'City')),
                TextField(controller: state, decoration: const InputDecoration(labelText: 'State')),
                TextField(controller: country, decoration: const InputDecoration(labelText: 'Country')),
                TextField(controller: postal, decoration: const InputDecoration(labelText: 'Postal code')),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
            FilledButton(
              onPressed: () {
                if (line1.text.trim().isEmpty) return;
                Navigator.pop(ctx, true);
              },
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );
    if (ok != true || !mounted) {
      line1.dispose(); city.dispose(); state.dispose(); country.dispose(); postal.dispose();
      return;
    }
    try {
      await _service.addAddress(
        widget.customerId,
        addressLine1: line1.text.trim(),
        addressType: type,
        city: city.text.trim().isEmpty ? null : city.text.trim(),
        state: state.text.trim().isEmpty ? null : state.text.trim(),
        country: country.text.trim().isEmpty ? null : country.text.trim(),
        postalCode: postal.text.trim().isEmpty ? null : postal.text.trim(),
      );
      line1.dispose(); city.dispose(); state.dispose(); country.dispose(); postal.dispose();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Address added')));
      await _load();
    } catch (e) {
      line1.dispose(); city.dispose(); state.dispose(); country.dispose(); postal.dispose();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    }
  }

  Future<void> _changeStatus(String newStatus) async {
    if (_customer == null || _customer!.status == newStatus) return;
    try {
      await _service.update(widget.customerId, status: newStatus);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Status updated to $newStatus')),
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
    if (_loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (_error != null || _customer == null) {
      return Scaffold(appBar: AppBar(), body: Center(child: Text(_error ?? 'Not found')));
    }
    final c = _customer!;
    final canEdit = CrmRbac.canUpdateCustomer(context.watch<AuthController>().profile);
    final hasOpportunity = context.watch<EditionController>().hasOpportunity;
    final hasSalQuote = context.watch<EditionController>().hasSalQuote;
    return Scaffold(
      appBar: AppBar(
        title: Text(c.customerNumber),
        actions: [
          IconButton(tooltip: 'Refresh', onPressed: _load, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(CrmSpacing.page),
        children: [
          Text(c.legalName, style: Theme.of(context).textTheme.headlineSmall),
          if (c.tradeName != null) Text(c.tradeName!),
          const SizedBox(height: CrmSpacing.md),
          if (canEdit)
            DropdownButtonFormField<String>(
              value: c.status,
              decoration: const InputDecoration(labelText: 'Status'),
              items: const [
                'PROSPECT',
                'ACTIVE',
                'INACTIVE',
                'ON_HOLD',
                'SUSPENDED',
                'CANCELLED',
              ].map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
              onChanged: (v) {
                if (v != null) _changeStatus(v);
              },
            )
          else
            Text('Status: ${c.status}'),
          Text('Type: ${c.customerType}'),
          if (c.notes != null) ...[
            const SizedBox(height: CrmSpacing.sm),
            Text(c.notes!),
          ],
          const SizedBox(height: CrmSpacing.md),
          CrmSectionCard(
            title: 'Contacts',
            trailing: canEdit
                ? TextButton.icon(
                    onPressed: _addContact,
                    icon: const Icon(Icons.add, size: 18),
                    label: const Text('Add'),
                  )
                : null,
            child: c.contacts.isEmpty
                ? const Text('No contacts yet.')
                : Column(
                    children: c.contacts
                        .map(
                          (contact) => ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.person_outline),
                            title: Text(contact.displayName),
                            subtitle: Text(
                              [
                                if (contact.email != null) contact.email,
                                if (contact.phoneMobile != null) contact.phoneMobile,
                              ].whereType<String>().join(' · '),
                            ),
                            trailing: contact.isPrimary
                                ? const Chip(label: Text('Primary'))
                                : null,
                          ),
                        )
                        .toList(),
                  ),
          ),
          const SizedBox(height: CrmSpacing.sm),
          CrmSectionCard(
            title: 'Addresses',
            trailing: canEdit
                ? TextButton.icon(
                    onPressed: _addAddress,
                    icon: const Icon(Icons.add, size: 18),
                    label: const Text('Add'),
                  )
                : null,
            child: c.addresses.isEmpty
                ? const Text('No addresses yet.')
                : Column(
                    children: c.addresses
                        .map(
                          (addr) => ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.location_on_outlined),
                            title: Text(addr.addressType.replaceAll('_', ' ')),
                            subtitle: Text(addr.summary),
                          ),
                        )
                        .toList(),
                  ),
          ),
          if (hasOpportunity) ...[
            const SizedBox(height: CrmSpacing.sm),
            CrmSectionCard(
              title: 'Opportunities',
              child: _loadingOpps
                  ? const Center(child: Padding(
                      padding: EdgeInsets.all(CrmSpacing.md),
                      child: CircularProgressIndicator(),
                    ))
                  : _opportunities.isEmpty
                      ? const Text('No linked opportunities.')
                      : Column(
                          children: _opportunities
                              .map(
                                (opp) => ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  leading: const Icon(Icons.trending_up_outlined),
                                  title: Text(opp.name),
                                  subtitle: Text(
                                    '${opp.opportunityNumber} · ${opp.stage} · ${opp.status}',
                                  ),
                                  onTap: () => context.push(
                                    CrmRoutes.opportunityDetail(opp.opportunityId),
                                  ),
                                ),
                              )
                              .toList(),
                        ),
            ),
          ],
          if (hasSalQuote) ...[
            const SizedBox(height: CrmSpacing.sm),
            CrmSectionCard(
              title: 'Sales',
              child: ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.receipt_long_outlined),
                title: const Text('Sales orders'),
                subtitle: const Text('Orders linked to this customer'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.go(
                  CrmRoutes.salesOrdersFiltered(customerId: c.customerId),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
