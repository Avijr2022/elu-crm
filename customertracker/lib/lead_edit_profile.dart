import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class LeadEditprofile extends StatelessWidget {
  const LeadEditprofile({super.key});

  @override
  Widget build(BuildContext context) {
    const appTitle = 'Edit Lead';
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: appTitle,
      home: Scaffold(
        resizeToAvoidBottomInset: true,
        appBar: AppBar(
          backgroundColor: const Color.fromARGB(255, 91, 92, 92),
          actions: <Widget>[
            Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {},
                  child: const Icon(Icons.save),
                )),
          ],
          title: const Text(
            appTitle,
          ),
          leading: IconButton(
              onPressed: () {
                Navigator.pop(context);
              },
              icon: const Icon(
                Icons.arrow_back_ios,
                size: 20,
                color: Color.fromARGB(255, 252, 250, 250),
              )),
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
          child: const MyCustomForm(),
        ),
      ),
    );
  }
}

class MyCustomForm extends StatefulWidget {
  const MyCustomForm({super.key});

  @override
  MyCustomFormState createState() {
    return MyCustomFormState();
  }
}

class MyCustomFormState extends State<MyCustomForm> {
  final _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Center(
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Container(
                decoration: const BoxDecoration(
                  image: DecorationImage(
                    image: AssetImage('assets/images/cover.jpg'),
                    fit: BoxFit.cover,
                  ),
                  color: Color.fromARGB(100, 229, 238, 144),
                ),
                child: const CircleAvatar(
                  backgroundColor: Color.fromARGB(100, 229, 238, 144),
                  minRadius: 44.0,
                  child: Center(
                    child: CircleAvatar(
                      radius: 38.0,
                      backgroundColor: Color.fromARGB(100, 220, 228, 149),
                      backgroundImage: null,
                      child: ClipOval(
                        child: SizedBox(
                          width: 180.0,
                          height: 180.0,
                          child: Icon(Icons.camera_alt),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              const Divider(
                color: Color.fromARGB(255, 91, 92, 92),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: TextFormField(
                  decoration: const InputDecoration(
                    icon: Icon(Icons.person),
                    hintText: 'Enter your First Name',
                    labelText: 'First Name',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(Icons.person),
                    hintText: 'Enter your Last Name',
                    labelText: 'Last Name',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(FontAwesomeIcons.userTie),
                    hintText: 'Enter your Designation',
                    labelText: 'Designation',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(FontAwesomeIcons.addressCard),
                    hintText: 'Enter your Organisation Name',
                    labelText: 'Organisation Name',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(Icons.web),
                    hintText: 'Organisation website',
                    labelText: 'Organisation website',
                  ),
                ),
                // const Divider(
                //   color: Color.fromARGB(255, 42, 90, 250),
                // ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(Icons.email),
                    hintText: 'Enter a email address',
                    labelText: 'Email',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(Icons.phone),
                    hintText: 'Enter a phone number',
                    labelText: 'Phone',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(FontAwesomeIcons.mapPin),
                    hintText: 'Address line 1',
                    labelText: 'Address line 1',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(Icons.alt_route),
                    hintText: 'Address line 2',
                    labelText: 'Address line 2',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(Icons.location_city),
                    hintText: 'Enter your City',
                    labelText: 'City',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(Icons.gps_fixed),
                    hintText: 'Enter your State',
                    labelText: 'State',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(Icons.pin_drop_outlined),
                    hintText: 'Enter your ZIP Code',
                    labelText: 'ZIP',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(FontAwesomeIcons.globe),
                    hintText: 'Enter your Country',
                    labelText: 'Country',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(FontAwesomeIcons.gitlab),
                    hintText: 'Gitlab URL',
                    labelText: 'Gitlab URL',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(FontAwesomeIcons.twitter),
                    hintText: 'Twitter URL',
                    labelText: 'Twitter URL',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(Icons.facebook),
                    hintText: 'Facebook URL',
                    labelText: 'Facebook URL',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(FontAwesomeIcons.instagram),
                    hintText: 'Instagram URL',
                    labelText: 'Instagram URL',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: const TextField(
                  decoration: InputDecoration(
                    icon: Icon(Icons.account_box),
                    hintText: 'Account Owner',
                    labelText: 'Account Owner',
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
