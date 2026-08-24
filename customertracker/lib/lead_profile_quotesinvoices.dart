// ignore_for_file: sort_child_properties_last, unused_field, no_leading_underscores_for_local_identifiers, unused_local_variable, unused_element, non_constant_identifier_names, use_key_in_widget_constructors, no_logic_in_create_state, unnecessary_const, avoid_print, prefer_typing_uninitialized_variables, unused_import, unnecessary_string_interpolations, unused_label

// import 'package:customertracker/buttontoggleswitch.dart';
// import 'package:customertracker/add_lead.dart';
import 'package:customertracker/lead_quotesinvoices_settings.dart';
import 'package:customertracker/side_menu_app.dart';
import 'package:customertracker/widgets/my_text_field.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class LeadProfileQuotesInvoices extends StatefulWidget {
  const LeadProfileQuotesInvoices({super.key});
  @override
  State<LeadProfileQuotesInvoices> createState() =>
      LeadProfileQuotesInvoicesState();
}

class LeadProfileQuotesInvoicesState extends State<LeadProfileQuotesInvoices> {
  bool isToggled = false;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: DefaultTabController(
        length: 2,
        child: Scaffold(
          appBar: AppBar(
            leading: Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {
                    Navigator.pop(context);
                  },
                  child: const Icon(Icons.arrow_back_ios_new),
                )),
            backgroundColor: const Color.fromARGB(255, 91, 92, 92),
            bottom: const TabBar(
              tabs: [
                Tab(icon: Icon(Icons.request_quote_outlined)),
                Tab(icon: Icon(Icons.summarize)),
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
                              builder: (context) =>
                                  const QuoteSettingLayout()));
                    },
                    child: const Icon(
                      Icons.settings,
                      size: 20.0,
                    ),
                  )),
            ],
            title: const Text('Quotes & Invoices'),
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
                QuotesNotification(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class QuotesNotification extends StatelessWidget {
  const QuotesNotification({super.key});

  @override
  Widget build(BuildContext context) {
    double _height = 100.0;

    final List<String> quot_number = <String>[
      'Quotation #1234567891',
      'Quotation #1234567892',
    ];
    final List<String> lead_name = <String>[
      "Amalendu Chatterjee, EIIPL",
      "Ranadeep Dhar, WTL",
    ];
    final List<String> coordinator_name = <String>[
      "Tarak Basak",
      "Avik Dey",
    ];
    final List<String> current_date = <String>[
      "23-Mar-2023",
      "22-Mar-2023",
    ];
    final List<String> quote_amount = <String>[
      "Rs. 10,500",
      "Rs. 90,000",
    ];

    void onClick() {
      if (_height == 60) {
        setState(() {
          _height = 100.0;
        });
      } else {
        setState(() {
          _height = 60;
        });
      }
    }

    return Scaffold(
      backgroundColor: const Color.fromARGB(110, 255, 255, 255),
      body: ListView.separated(
        shrinkWrap: true,
        padding: const EdgeInsets.all(8),
        itemCount: quot_number.length,
        itemBuilder: (BuildContext context, int index) {
          return Card(
            color: const Color.fromARGB(251, 250, 250, 249),
            borderOnForeground: true,
            elevation: 8,
            child: SizedBox(
              height: _height,
              child: Column(
                mainAxisSize: MainAxisSize.max,
                children: <Widget>[
                  InkWell(
                    onTap: () {
                      onClick();
                    },
                    onDoubleTap: () {
                      print("Good Job");
                    },
                    child: ListTile(
                      leading: const Icon(
                        Icons.chat_rounded,
                        size: 30,
                      ),
                      // const CircleAvatar(
                      //   backgroundImage: AssetImage('assets/images/cover.jpg'),
                      // ),
                      title: Text(
                          "${quot_number[index]}              ${current_date[index]}\n${lead_name[index]}            ${quote_amount[index]}",
                          style: const TextStyle(
                              fontSize: 12,
                              color: Color.fromARGB(255, 0, 0, 0))),
                      subtitle: Text(
                        "${coordinator_name[index]}",
                        style: const TextStyle(
                            color: Color.fromARGB(255, 13, 31, 110)),
                      ),
                    ),
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: <Widget>[
                      IconButton(
                        onPressed: () {},
                        icon: const Icon(
                          Icons.edit,
                          color: Color.fromARGB(255, 154, 156, 15),
                        ),
                      ),
                      const SizedBox(width: 40),
                      IconButton(
                        onPressed: () {},
                        icon: const Icon(
                          Icons.copy,
                          color: Color.fromARGB(255, 224, 152, 18),
                        ),
                      ),
                      const SizedBox(width: 40),
                      IconButton(
                        onPressed: () {},
                        icon: const Icon(
                          Icons.delete,
                          color: Color.fromARGB(255, 214, 59, 11),
                        ),
                      ),
                      const SizedBox(width: 40),
                      IconButton(
                        onPressed: () {},
                        icon: const Icon(Icons.remove_red_eye_outlined),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        },
        separatorBuilder: (BuildContext context, int index) => const Divider(),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Add your onPressed code here!
        },
        backgroundColor: Colors.green,
        child: const Icon(
          Icons.add,
          size: 30,
        ),
      ),
    );
  }

  void setState(Null Function() param0) {}
}
