// ignore_for_file: non_constant_identifier_names, file_names

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class Loginotp extends StatelessWidget {
  static String id = 'Login-OTP';

  const Loginotp({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 249, 249, 250),
      appBar: AppBar(
        title: const Text(
          'Euphoria Infotech (I) Pvt Ltd',
          style: TextStyle(fontSize: 17),
        ),
        elevation: 0,
        backgroundColor: const Color.fromARGB(255, 91, 92, 92),
        leading: IconButton(
            onPressed: () {
              Navigator.pop(context);
            },
            icon: const Icon(
              Icons.arrow_back_ios,
              size: 20,
              color: Color.fromARGB(255, 250, 248, 248),
            )),
        systemOverlayStyle: SystemUiOverlayStyle.dark,
      ),
      body: Container(
        padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
        height: 700,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/cover.jpg'),
            fit: BoxFit.cover,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 10.0),
          child: Column(
            // mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 30),
              const Text(
                textAlign: TextAlign.center,
                'Login using OTP',
                style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                    color: Color.fromARGB(255, 5, 5, 5)),
              ),
              const SizedBox(height: 30),
              const Text(
                textAlign: TextAlign.center,
                'Login OTP will be sent via email and SMS',
                style: TextStyle(
                    fontSize: 12, color: Color.fromARGB(255, 10, 10, 10)),
              ),
              const SizedBox(height: 50),
              TextFormField(
                style: const TextStyle(color: Color.fromARGB(255, 10, 10, 10)),
                decoration: const InputDecoration(
                  labelText: 'Registered Email',
                  prefixIcon: Icon(
                    Icons.mail,
                    color: Color.fromARGB(255, 8, 8, 8),
                  ),
                  errorStyle: TextStyle(color: Color.fromARGB(255, 8, 8, 8)),
                  labelStyle: TextStyle(color: Color.fromARGB(255, 10, 10, 10)),
                  hintStyle: TextStyle(color: Color.fromARGB(255, 5, 5, 5)),
                  focusedBorder: UnderlineInputBorder(
                    borderSide: BorderSide(color: Color.fromARGB(255, 8, 8, 8)),
                  ),
                  enabledBorder: UnderlineInputBorder(
                    borderSide:
                        BorderSide(color: Color.fromARGB(255, 10, 10, 10)),
                  ),
                  errorBorder: UnderlineInputBorder(
                    borderSide:
                        BorderSide(color: Color.fromARGB(255, 10, 10, 10)),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              TextButton(
                onPressed: () {},
                child: const Text(
                  'SEND OTP CODE',
                  style: TextStyle(
                      fontSize: 15, color: Color.fromARGB(255, 5, 5, 5)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
