// ignore_for_file: depend_on_referenced_packages, duplicate_import, unused_import

import 'package:customertracker/screens/home_page.dart';
import 'package:customertracker/theme/colors/light_colors.dart';
import 'package:flutter/material.dart';
import 'package:customertracker/screens/home_page.dart';
import 'package:customertracker/theme/colors/light_colors.dart';
import 'package:flutter/services.dart';

void main() {
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    systemNavigationBarColor: LightColors.kLightYellow, // navigation bar color
    statusBarColor: Color(0xffffb969), // status bar color
  ));

  return runApp(const LeadCalendar());
}

class LeadCalendar extends StatelessWidget {
  const LeadCalendar({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      // title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        textTheme: Theme.of(context).textTheme.apply(
            bodyColor: LightColors.kDarkBlue,
            displayColor: LightColors.kDarkBlue,
            fontFamily: 'EIIPL'),
      ),
      home: const HomePage(),
      debugShowCheckedModeBanner: false,
    );
  }
}
