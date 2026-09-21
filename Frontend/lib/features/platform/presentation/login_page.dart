import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/auth/auth_controller.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  // Demo credentials are a local-development convenience only. Putting them
  // behind kDebugMode (a compile-time constant) keeps them out of release
  // builds entirely instead of merely hiding them at runtime.
  static const String _demoTenant = kDebugMode ? 'EIIP001' : '';
  static const String _subtitle =
      kDebugMode ? 'Euphoria Infotech · Local Dev' : 'Euphoria Infotech';
  static const String _demoEmail =
      kDebugMode ? 'admin@euphoriainfotech.com' : '';
  static const String _demoPassword = kDebugMode ? 'Admin@12345' : '';

  final _formKey = GlobalKey<FormState>();
  final _tenantCtrl = TextEditingController(text: _demoTenant);
  final _emailCtrl = TextEditingController(text: _demoEmail);
  final _passwordCtrl = TextEditingController(text: _demoPassword);

  @override
  void dispose() {
    _tenantCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();

    return Scaffold(
      body: Container(
        width: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0B3D91), Color(0xFF1F6FEB), Color(0xFFE8F1FF)],
          ),
        ),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: Card(
              elevation: 8,
              margin: const EdgeInsets.all(24),
              child: Padding(
                padding: const EdgeInsets.all(28),
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'E-LinkUp',
                        textAlign: TextAlign.center,
                        style: Theme.of(context)
                            .textTheme
                            .headlineMedium
                            ?.copyWith(
                              fontWeight: FontWeight.w700,
                              color: const Color(0xFF0B3D91),
                            ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _subtitle,
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      const SizedBox(height: 24),
                      TextFormField(
                        controller: _tenantCtrl,
                        decoration: const InputDecoration(
                          labelText: 'Tenant code',
                          hintText: kDebugMode ? 'EIIP001' : null,
                        ),
                        validator: (v) =>
                            (v == null || v.isEmpty) ? 'Required' : null,
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _emailCtrl,
                        decoration: const InputDecoration(labelText: 'Email'),
                        validator: (v) =>
                            (v == null || v.isEmpty) ? 'Required' : null,
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _passwordCtrl,
                        obscureText: true,
                        decoration:
                            const InputDecoration(labelText: 'Password'),
                        validator: (v) =>
                            (v == null || v.length < 8) ? 'Min 8 chars' : null,
                      ),
                      if (auth.error != null) ...[
                        const SizedBox(height: 12),
                        Text(
                          auth.error!,
                          style: const TextStyle(color: Colors.red),
                        ),
                      ],
                      const SizedBox(height: 20),
                      FilledButton(
                        onPressed: auth.busy
                            ? null
                            : () async {
                                if (!_formKey.currentState!.validate()) return;
                                await auth.login(
                                  email: _emailCtrl.text.trim(),
                                  password: _passwordCtrl.text,
                                  tenantCode:
                                      _tenantCtrl.text.trim().toUpperCase(),
                                );
                              },
                        child: auth.busy
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child:
                                    CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Text('Sign in'),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Defaults: INR · Asia/Kolkata · FY Apr–Mar',
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
