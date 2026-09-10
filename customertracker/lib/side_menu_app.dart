// ignore_for_file: sort_child_properties_last, prefer_const_constructors, unused_import, duplicate_ignore

// ignore: unused_import

// ignore: unused_import
import 'package:customertracker/buttontoggleswitch.dart';
import 'package:customertracker/lead_category.dart';
import 'package:customertracker/lead_event_calendar.dart';
// import 'package:customertracker/lead_add_followup.dart';
import 'package:customertracker/home.dart';
import 'package:customertracker/screens/payment_receipts_list.dart';
import 'package:customertracker/lead_report.dart';
import 'package:customertracker/main.dart';
import 'package:customertracker/my_profile.dart';
import 'package:customertracker/user.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'add_lead.dart';
import 'lead_state.dart';
import 'settings.dart';
import 'package:customertracker/screens/branding_primary_color.dart';

class NavDrawer extends StatelessWidget {
  const NavDrawer({super.key});

  get firstCamera => null;

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: <Widget>[
          const UserAccountsDrawerHeader(
            accountName: Text(
              'Kedar Gupta',
              style: TextStyle(
                color: Color.fromARGB(248, 255, 254, 254),
                fontSize: 25.0,
              ),
            ),
            accountEmail: Text(
              'kedargupta@gmail.com',
              style: TextStyle(
                  color: Color.fromARGB(179, 8, 8, 8), fontSize: 15.0),
            ),
            currentAccountPicture: CircleAvatar(
              backgroundColor: Color.fromARGB(179, 227, 247, 173),
              minRadius: 41.0,
              child: CircleAvatar(
                radius: 28.0,
                backgroundImage: AssetImage('assets/images/kedargupta.jpg'),
                // NetworkImage(''),
              ),
            ),
            decoration: BoxDecoration(
                color: Color.fromARGB(255, 250, 251, 252),
                image: DecorationImage(
                    fit: BoxFit.fill,
                    image: AssetImage('assets/images/cover.jpg'))),
          ),
          ListTile(
            leading: const Icon(Icons.input),
            title: const Text('Home Page'),
            onTap: () => {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const LeadCalendar()))
            },
          ),
          ListTile(
            leading: const Icon(Icons.category),
            title: const Text('Lead Category'),
            onTap: () => {
              Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => LeadCategory(),
                  )),
            },
          ),
          ListTile(
            leading: const Icon(Icons.precision_manufacturing_outlined),
            title: const Text('User Profile'),
            onTap: () => {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const UsersForm()))
            },
          ),
          ListTile(
            leading: const Icon(Icons.area_chart_outlined),
            title: const Text('Report'),
            onTap: () => {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const LeadReport()))
            },
          ),
          ListTile(
            leading: const Icon(Icons.verified_user),
            title: const Text('My Profile'),
            onTap: () => {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const myprofile()))
            },
          ),
          ListTile(
            leading: const Icon(Icons.people_alt),
            title: const Text('Leads'),
            onTap: () => {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const Leadstate()))
            },
          ),
          ListTile(
            leading: const Icon(Icons.person_add_alt),
            title: const Text('Add Leads'),
            onTap: () => {
              Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => const Addleadbarstate()))
            },
          ),
          ListTile(
            leading: const Icon(Icons.receipt_long),
            title: const Text('Payment Receipts'),
            onTap: () => {
              Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (context) => const PaymentReceiptsList()),
              )
            },
          ),
          ListTile(
            leading: const Icon(Icons.settings),
            title: const Text('Settings'),
            onTap: () => {
              Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => const SettingsLayout()))
            },
          ),
          ListTile(
            leading: const Icon(Icons.color_lens),
            title: const Text('Branding - Primary Color'),
            onTap: () => {
              Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (context) => const BrandingPrimaryColorScreen()),
              )
            },
          ),
          ListTile(
            leading: const Icon(FontAwesomeIcons.hubspot),
            title: const Text('My Creation Hub'),
            onTap: () => {
              // Navigator.push(context,
              //     MaterialPageRoute(builder: (context) => FollowupLayout()))
            },
          ),
          ListTile(
            leading: const Icon(Icons.exit_to_app),
            title: const Text('Logout'),
            onTap: () => {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => const MyApp()))
            },
          ),
        ],
      ),
    );
  }
}
