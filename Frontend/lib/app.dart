import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'core/auth/auth_controller.dart';
import 'core/edition/edition_controller.dart';
import 'core/routing/app_router.dart';

class ElinkupApp extends StatefulWidget {
  const ElinkupApp({super.key});

  @override
  State<ElinkupApp> createState() => _ElinkupAppState();
}

class _ElinkupAppState extends State<ElinkupApp> {
  late final AuthController _auth;
  late final EditionController _edition;
  late final GoRouter _router;

  @override
  void initState() {
    super.initState();
    _auth = AuthController();
    _edition = EditionController();
    _router = createAppRouter(_auth, _edition);
    _auth.addListener(_onAuthChange);
    _auth.bootstrap().then((_) {
      if (mounted && _auth.isAuthenticated) _edition.load();
    });
  }

  void _onAuthChange() {
    if (_auth.isAuthenticated) {
      _edition.clear();
      _edition.load();
    } else {
      _edition.clear();
    }
  }

  @override
  void dispose() {
    _auth.removeListener(_onAuthChange);
    _auth.dispose();
    _edition.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: _auth),
        ChangeNotifierProvider.value(value: _edition),
      ],
      child: MaterialApp.router(
        title: 'E-LinkUp',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF0B3D91),
            brightness: Brightness.light,
          ),
          useMaterial3: true,
          inputDecorationTheme: const InputDecorationTheme(border: OutlineInputBorder()),
        ),
        routerConfig: _router,
        builder: (context, child) {
          return ListenableBuilder(
            listenable: _auth,
            builder: (context, _) {
              if (_auth.booting) {
                return const Scaffold(
                  body: Center(child: CircularProgressIndicator()),
                );
              }
              return child ?? const SizedBox.shrink();
            },
          );
        },
      ),
    );
  }
}
