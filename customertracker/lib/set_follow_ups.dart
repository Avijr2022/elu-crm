// ignore_for_file: prefer_typing_uninitialized_variables, avoid_print

import 'package:customertracker/lead_profile_add_followup.dart';
import 'package:customertracker/lead_set_followup_search.dart';

import 'package:flutter/material.dart';

void main() => runApp(const FollowUps());

class FollowUps extends StatelessWidget {
  static var data;

  const FollowUps({super.key});

  @override
  Widget build(BuildContext context) {
    // const title = 'Contact List';

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      // title: title,
      home: Scaffold(
        appBar: AppBar(
          title: const Text('Set Follow-up'),
          backgroundColor: const Color.fromARGB(255, 91, 92, 92),
          leading: IconButton(
              onPressed: () {
                Navigator.pop(context);
              },
              icon: const Icon(
                Icons.arrow_back_ios,
                size: 15,
                color: Color.fromARGB(255, 248, 247, 247),
              )),
          actions: <Widget>[
            Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const SearchPage2()));
                  },
                  child: const Icon(
                    Icons.search,
                    size: 15.0,
                  ),
                )),
          ],
        ),
        body: Container(
          padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
          height: 1000,
          decoration: const BoxDecoration(
            image: DecorationImage(
              image: AssetImage('assets/images/cover2.jpg'),
              fit: BoxFit.cover,
            ),
          ),
          child: ListView(
            children: <Widget>[
              ListTile(
                leading: const CircleAvatar(
                  // backgroundColor: Colors.white,
                  backgroundImage: AssetImage('assets/images/amalda.jpg'),
                ),
                title: const Text(
                  'Amalendu Chatterjee',
                ),
                subtitle: const Text('+91 98361 77764'),
                trailing: const Icon(Icons.keyboard_arrow_right),
                onTap: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const PeofileFollowupLayout()));
                },
              ),
              const Divider(
                height: 1.0,
                indent: 1.0,
              ),
              ListTile(
                leading: const CircleAvatar(
                  // backgroundColor: Colors.white,
                  backgroundImage: AssetImage('assets/images/rana.jpg'),
                ),
                title: const Text('Ranadeep Dhar'),
                subtitle: const Text('+91 92313 42284'),
                trailing: const Icon(Icons.keyboard_arrow_right),
                onTap: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const PeofileFollowupLayout()));
                },
                onLongPress: () {
                  const Text('Data');
                },
              ),
              const Divider(
                height: 1.0,
                indent: 1.0,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
