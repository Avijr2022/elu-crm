// ignore_for_file: prefer_typing_uninitialized_variables, unnecessary_string_interpolations

import 'package:flutter/material.dart';

void main() => runApp(const LeadNotification());

// ignore: camel_case_types
class LeadNotification extends StatelessWidget {
  const LeadNotification({super.key});

  @override
  Widget build(BuildContext context) {
    const title = 'Notification';

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: title,
      home: Scaffold(
        appBar: AppBar(
          title: const Text(
            "Kedar Gupta",
            style: TextStyle(color: Color.fromARGB(255, 250, 249, 249)),
          ),
          leading: const CircleAvatar(
            backgroundColor: Color.fromARGB(100, 255, 255, 255),
            minRadius: 10.0,
            child: CircleAvatar(
                radius: 25.0,
                backgroundImage: AssetImage('assets/images/kedargupta.jpg')
                // NetworkImage(''),
                ),
          ),
          backgroundColor: const Color.fromARGB(100, 22, 44, 33),
          actions: <Widget>[
            Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {},
                  child: const Icon(
                    Icons.notifications,
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
          child: const MyStatelessWidget(),
        ),
      ),
    );
  }
}

class MyStatelessWidget extends StatelessWidget {
  const MyStatelessWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final List<String> msg = <String>[
      'Please co-ordinate accordingly. Please co-ordinate accordingly',
      'Update user.',
      'Arrange a meeting.',
      'Immidiate response.',
      'Immidiate response required.',
    ];
    final List<String> time = <String>[
      "5 days ago",
      "5 hours ago",
      "1 week ago",
      "5 minutes ago",
      "8 minutes ago",
    ];

    return ListView.separated(
      shrinkWrap: true,
      padding: const EdgeInsets.all(8),
      itemCount: msg.length,
      itemBuilder: (BuildContext context, int index) {
        return Card(
          color: const Color.fromARGB(111, 243, 240, 76),
          borderOnForeground: true,
          elevation: 8,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              ListTile(
                leading: const CircleAvatar(
                  backgroundImage: AssetImage('assets/images/cover.jpg'),
                ),
                title: Text("${msg[index]}",
                    style: const TextStyle(
                        color: Color.fromARGB(255, 247, 248, 247))),
                subtitle: Text(
                  "${time[index]}",
                  style: const TextStyle(color: Colors.orangeAccent),
                ),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: <Widget>[
                  TextButton(
                    child: const Text('Share'),
                    onPressed: () {/* ... */},
                  ),
                  const SizedBox(width: 5),
                  TextButton(
                    child: const Text('Remove'),
                    onPressed: () {/* ... */},
                  ),
                ],
              ),
            ],
          ),
        );
      },
      separatorBuilder: (BuildContext context, int index) => const Divider(),
    );
  }
}
