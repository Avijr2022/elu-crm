// ignore_for_file: prefer_typing_uninitialized_variables

import 'package:customertracker/add_lead.dart';
import 'package:flutter/material.dart';

void main() => runApp(const ListApp());

class ListApp extends StatelessWidget {
  static var data;

  const ListApp({super.key});

  @override
  Widget build(BuildContext context) {
    const title = 'Contact List';

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: title,
      home: Scaffold(
        appBar: AppBar(
          title: const Text(
            "All leads",
            style: TextStyle(color: Color.fromARGB(255, 250, 249, 249)),
          ),
          leading: const Icon(
            Icons.list,
            color: Color.fromARGB(255, 249, 250, 250),
          ),
          // title: const Text(title),

          backgroundColor: const Color.fromARGB(100, 22, 44, 33),
          actions: <Widget>[
            Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {},
                  child: const Icon(
                    Icons.groups_outlined,
                    color: Color.fromARGB(255, 252, 252, 252),
                    size: 25.0,
                  ),
                )),
            Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {},
                  child: const Icon(
                    Icons.arrow_drop_down,
                    color: Color.fromARGB(255, 255, 255, 255),
                    size: 25.0,
                  ),
                )),
          ],
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
          child: ListView(
            children: <Widget>[
              ListTile(
                leading: const CircleAvatar(
                  // backgroundColor: Colors.white,
                  backgroundImage: AssetImage('assets/images/amalda.jpg'),
                ),
                title: const Text(
                  'Amalendu Chatterjee',
                  style: TextStyle(fontStyle: FontStyle.italic),
                ),
                subtitle: const Text('+91 98361 77764'),
                trailing: const Icon(Icons.keyboard_arrow_right),
                onTap: () {
                  const Text('Another data');
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
                title: const Text(
                  'Ranadeep Dhar',
                  style: TextStyle(fontStyle: FontStyle.italic),
                ),
                subtitle: const Text('+91 92313 42284'),
                trailing: const Icon(Icons.keyboard_arrow_right),
                onTap: () {
                  const Text('Another data');
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
        floatingActionButton: FloatingActionButton.small(
          onPressed: () {
            Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (context) => const Addleadbarstate()));
          },
          backgroundColor: const Color.fromARGB(255, 91, 92, 92),
          child: const Icon(Icons.add),
        ),
      ),
    );
  }
}
