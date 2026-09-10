// ignore_for_file: constant_identifier_names, duplicate_ignore, avoid_print

// ignore: unused_import
import 'package:customertracker/lead_report_pyramid.dart';
import 'package:customertracker/side_menu_app.dart';
import 'package:flutter/material.dart';

class LeadReport extends StatelessWidget {
  const LeadReport({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: DefaultTabController(
        length: 4,
        child: Scaffold(
          drawer: const NavDrawer(),
          appBar: AppBar(
            bottom: const TabBar(
              tabs: [
                Tab(icon: Icon(Icons.network_wifi_outlined)),
                Tab(icon: Icon(Icons.star_half)),
                Tab(icon: Icon(Icons.lan_outlined)),
                Tab(icon: Icon(Icons.leaderboard)),
              ],
            ),
            title: const Text('Reports'),
          ),
          body: const TabBarView(
            children: <Widget>[
              // ChartData,
              Icon(Icons.network_wifi_outlined),
              Icon(Icons.star_half),
              Icon(Icons.lan_outlined),
              Icon(Icons.leaderboard),
            ],
          ),
        ),
      ),
    );
  }
}
