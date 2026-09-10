// ignore_for_file: unused_import

import 'package:customertracker/lead_contact_norms.dart';
import 'package:customertracker/lead_contacts.dart';
import 'package:customertracker/lead_filter.dart';
import 'package:customertracker/lead_map.dart';
import 'package:customertracker/lead_notification.dart';
import 'package:customertracker/lead_report.dart';
import 'package:customertracker/search_lead.dart';
import 'package:customertracker/lead_search.dart';
import 'package:customertracker/side_menu_app.dart';
import 'package:customertracker/lead_contacts_old.dart';
import 'package:customertracker/lead_table_event_calendar.dart';
import 'package:customertracker/utils.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class Leadstate extends StatelessWidget {
  const Leadstate({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: DefaultTabController(
        length: 3,
        child: Scaffold(
          drawer: const NavDrawer(),
          appBar: AppBar(
            backgroundColor: const Color.fromARGB(255, 91, 92, 92),
            bottom: const TabBar(
              tabs: [
                Tab(icon: Icon(Icons.groups)),
                Tab(icon: Icon(Icons.calendar_month)),
                Tab(icon: Icon(Icons.notifications_active)),
              ],
            ),
            actions: <Widget>[
              Padding(
                  padding: const EdgeInsets.only(right: 20.0),
                  child: GestureDetector(
                    onTap: () {
                      Navigator.push(
                          context,
                          MaterialPageRoute(
                              builder: (context) => const LeadSearch()));
                    },
                    child: const Icon(
                      Icons.search,
                      size: 20.0,
                    ),
                  )),
              Padding(
                  padding: const EdgeInsets.only(right: 20.0),
                  child: GestureDetector(
                    onTap: () {
                      showDialog(
                          context: context,
                          builder: (BuildContext context) {
                            return const AlertDialog(
                              backgroundColor:
                                  Color.fromARGB(178, 243, 252, 125),
                              title: Text("Filter"),
                            );
                          });
                    },
                    child: const Icon(
                      Icons.filter_alt_outlined,
                      size: 18.0,
                    ),
                  )),
              Padding(
                  padding: const EdgeInsets.only(right: 20.0),
                  child: GestureDetector(
                    onTap: () {
                      Navigator.push(
                          context,
                          MaterialPageRoute(
                              builder: (context) => const LeadReport()));
                    },
                    child: const Icon(
                      FontAwesomeIcons.chartPie,
                      size: 18.0,
                    ),
                  )),
              Padding(
                  padding: const EdgeInsets.only(right: 20.0),
                  child: GestureDetector(
                    onTap: () {
                      Navigator.push(
                          context,
                          MaterialPageRoute(
                              builder: (context) => const LeadMap()));
                    },
                    child: const Icon(
                      Icons.person_pin_circle,
                      size: 18.0,
                    ),
                  )),
            ],
            title: const Text('Leads'),
          ),
          body: Container(
            padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
            height: 1000,
            decoration: const BoxDecoration(
              image: DecorationImage(
                image: AssetImage('assets/images/cover.jpg'),
                fit: BoxFit.cover,
              ),
            ),
            // ignore: prefer_const_constructors
            child: TabBarView(
              children: const <Widget>[
                LeadContactNorms(),
                TableEventsCalendar(),
                LeadNotification(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
