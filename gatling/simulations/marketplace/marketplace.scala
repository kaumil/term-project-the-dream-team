/*
 * Copyright 2011-2020 GatlingCorp (https://gatling.io)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package marketplace

import scala.concurrent.duration._
import io.gatling.core.Predef._
import io.gatling.http.Predef._


object Utility {
  /*
    Utility to get an Int from an environment variable.
    Return defInt if the environment var does not exist
    or cannot be converted to a string.
  */
  def envVarToInt(ev: String, defInt: Int): Int = {
    try {
      sys.env(ev).toInt
    } catch {
      case e: Exception => defInt
    }
  }

  /*
    Utility to get an environment variable.
    Return defStr if the environment var does not exist.
  */
  def envVar(ev: String, defStr: String): String = {
    sys.env.getOrElse(ev, defStr)
  }
}

object Users {

    val users_feeder = csv("users.csv").random
    

    val createuser = forever("i") {
        feed(users_feeder)
        .exec(http("Request Name = Create User")
            .post("/api/v1/users/create_user/")
            .header("content-type","application/json")
            .body(StringBody(string = """{"users_id": "${users_id}",
                "username": "${username}",
                "password": "${password}",
                "users_role": "${users_role}",
                "disabled": "False"
            }"""))
            .check(status.not(500))
            .check(status.is(200)))
    }

    val userlogin = forever("i") {
        feed(users_feeder)
        .exec(http("Request Name = User Login")
            .put("/api/v1/users/login/")
            .header("content-type","application/json")
            .body(StringBody(string = """{"users_id": "${users_id}",
                "password": "${password}"
            }"""))
            .check(status.not(500))
            .check(status.is(200)))

    }

    val getuser = forever("i") {
        feed(users_feeder)
        .exec(http("Request Name = Get User")
            .get("/api/v1/users/get_user/${users_id}")
            .header("content-type","application/json")
            .check(status.not(500))
            .check(status.is(200)))

    }

    val updateuser = forever("i") {
        feed(users_feeder)
        .exec(http("Request Name = Update User")
            .put("/api/v1/users/update_user/${users_id}")
            .header("content-type","application/json")
            .body(StringBody(string = """{"users_id": "updated_user",
                "password": "updated_pass",
                "users_role": "buyer",
                "disabled": "False"
            }"""))
            .check(status.not(500))
            .check(status.is(200)))

    }

    val userlogoff = forever("i") {
        feed(users_feeder)
        .exec(http("Request Name = User Logoff")
            .put("/api/v1/users/logoff/")
            .header("content-type","application/json")
            .body(StringBody(string = """{"jwt": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZTAwMzhmZWEtZjllZC00YzY1LWFhMGUtZmMxODkyMDZmYWVlIiwidGltZSI6MTY0ODMzNzM5Ny41MDg3NTE2fQ.tCDLNp5KzSnOC7561Fdo4958Mg6g-4ugkVn4vFBoAOc"}"""))
            .check(status.not(500))
            .check(status.is(200)))

    }

    val deleteuser = forever("i") {
        feed(users_feeder)
        .exec(http("Request Name = Get User")
            .delete("/api/v1/users/delete_user/${users_id}")
            .header("content-type","application/json")
            .check(status.not(500))
            .check(status.is(200)))

    }
}


object Images {

    val images_feeder = csv("images.csv").random

    val createimage = forever("i") {
        feed(images_feeder)
        .exec(http("Request Name = Create Image")
            .post("/api/v1/images/create_image")
            .header("content-type","application/json")
            .body(StringBody(string = """{"images_id": "${images_id}",
                "users_id": "${users_id}"
            }"""))
            .check(status.not(500))
            .check(status.is(200)))

    }

    val getimage = forever("i") {
        feed(images_feeder)
        .exec(http("Request Name = Get Image")
            .get("/api/v1/images/read_image/${images_id}")
            .header("content-type","application/json")
            .check(status.not(500))
            .check(status.is(200)))
    }
    
    val updateimage = forever("i") {
        feed(images_feeder)
        .exec(http("Request Name = Update Image")
            .put("/api/v1/images/change_owner/${images_id}")
            .header("content-type","application/json")
            .body(StringBody(string = """{"users_id": "${users_id}"}"""))
            .check(status.not(500))
            .check(status.is(200)))
    }

    val deleteimage = forever("i") {
        feed(images_feeder)
        .exec(http("Request Name = Delete Image")
            .delete("/api/v1/images/delete_image/${images_id}")
            .header("content-type","application/json")
            .check(status.not(500))
            .check(status.is(200)))
    }
}


object Transactions {

    val transactions_feeder = csv("transactions.csv").random

    val createtransaction = forever("i") {
        feed(transactions_feeder)
        .exec(http("Request Name = Create Transaction")
            .post("/api/v1/transaction/create_transaction")
            .header("content-type","application/json")
            .body(StringBody(string = """{"transactions_id": "${transactions_id}",
                "seller_id": "${seller_id}",
                "images_id": "${images_id}",
                "sold": "False"
            }"""))
            .check(status.not(500))
            .check(status.is(200)))
    }

    val readtransaction = forever("i") {
        feed(transactions_feeder)
        .exec(http("Request Name = Read Transaction")
            .get("/api/v1/transaction/read_transaction/${transactions_id}")
            .header("content-type","application/json")
            .check(status.not(500))
            .check(status.is(200)))
    }

    val updatetransaction = forever("i") {
        feed(transactions_feeder)
        .exec(http("Request Name = Update Transaction")
            .put("/api/v1/transaction/change_transaction/${transactions_id}")
            .header("content-type","application/json")
            .body(StringBody(string = """{
                "buyer_id": "567dce7f-b7b4-4efd-b75e-2b98592abe6d",
                "sold": "buyer"
            }"""))
            .check(status.not(500))
            .check(status.is(200)))
    }

    val deletetransaction = forever("i") {
        feed(transactions_feeder)
        .exec(http("Request Name = Delete Transaction")
            .delete("/api/v1/transaction/read_transaction/${transactions_id}")
            .header("content-type","application/json")
            .check(status.not(500))
            .check(status.is(200)))
    }
}

class MarketplaceSim extends Simulation {
  val httpProtocol = http
    .baseUrl("http://" + Utility.envVar("CLUSTER_IP", "127.0.0.1") + "/")
    .acceptHeader("application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    .authorizationHeader("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZGJmYmMxYzAtMDc4My00ZWQ3LTlkNzgtMDhhYTRhMGNkYTAyIiwidGltZSI6MTYwNzM2NTU0NC42NzIwNTIxfQ.zL4i58j62q8mGUo5a0SQ7MHfukBUel8yl8jGT5XmBPo")
    .acceptLanguageHeader("en-US,en;q=0.5")
}




class CreateUserSim extends MarketplaceSim {
  val scnCreateUser = scenario("CreateUser")
                    .exec(Users.createuser)
                    .pause(10)
                    .exec(Users.userlogin)
                    .pause(10)
                    .exec(Users.getuser)
                    .pause(10)
                    .exec(Users.updateuser)
                    .pause(10)
                    .exec(Users.userlogoff)
                    .pause(10)
                    .exec(Users.deleteuser)
                    .pause(10)
                    // .exec(Users.userlogin)
                    // .exec(Users.getuser)
                    // .exec(Users.updateuser)
                    // .exec(Users.userlogoff)
                    // .exec(Users.deleteuser)

  val users = Utility.envVarToInt("USERS", 10)
  // val times = Utility.envVarToInt("TIMES", 10)
  // val ell = Utility.envVarToInt("EACHLEVELLASTING", 10)
  // val srl = Utility.envVarToInt("SEPERATEDBYRAMPLASTING", 10)
  // val sf = Utility.envVarToInt("STARTINGFROM", 10)

  setUp(
    // Add one user per 10 s up to specified value
    scnCreateUser.inject(atOnceUsers(users))
    // scnCreateUser.inject(rampConcurrentUsers(1).to(users).during(5*users))
    // scnCreateUser.inject(
    //   incrementUsersPerSec(users)
    //     .times(times)
    //     .eachLevelLasting(ell)
    //     .separatedByRampsLasting(srl)
    //     .startingFrom(sf)
    // )
  ).protocols(httpProtocol)
}



class CreateImageSim extends MarketplaceSim {
  val scnCreateImage = scenario("CreateImage")
                    .exec(Images.createimage, Images.getimage, Images.deleteimage)
                    // .exec(Images.getimage)
                    // .exec(Images.deleteimage)

  val users = Utility.envVarToInt("USERS", 10)

  setUp(
    // Add one user per 10 s up to specified value
    // scnCreateImage.inject(rampConcurrentUsers(1).to(users).during(5*users))
    scnCreateImage.inject(atOnceUsers(users))
  ).protocols(httpProtocol)
}



class CreateTransactionSim extends MarketplaceSim {
  val scnCreateTransaction = scenario("CreateTransaction")
                    .exec(Transactions.createtransaction, Transactions.readtransaction, Transactions.updatetransaction, Transactions.deletetransaction)
                    // .exec(Transactions.readtransaction)
                    // .exec(Transactions.updatetransaction)
                    // .exec(Transactions.deletetransaction)

  val users = Utility.envVarToInt("USERS", 10)
  setUp(
    // Add one user per 10 s up to specified value
    // scnCreateTransaction.inject(rampConcurrentUsers(1).to(users).during(2*users))
    scnCreateTransaction.inject(atOnceUsers(users))
  ).protocols(httpProtocol)
}


class LoadTestingSim extends MarketplaceSim {
  val LoadTest = scenario("CreateUser")
                    .exec(Users.createuser)
                    .pause(10)
                    .exec(Users.userlogin)
                    .pause(10)
                    .exec(Users.getuser)
                    .pause(10)
                    .exec(Users.updateuser)
                    .pause(10)
                    .exec(Users.userlogoff)
                    .pause(10)
                    .exec(Users.deleteuser)
                    .pause(10)
                    .exec(Images.createimage)
                    .pause(10)
                    .exec(Images.getimage)
                    .pause(10)
                    .exec(Images.deleteimage)
                    .pause(10)
                    .exec(Transactions.createtransaction)
                    .pause(10)
                    .exec(Transactions.readtransaction)
                    .pause(10)
                    .exec(Transactions.updatetransaction)
                    .pause(10)
                    .exec(Transactions.deletetransaction)
                    .pause(10)
  
  val users = Utility.envVarToInt("USERS", 10)
  setUp(
    LoadTest.inject(rampConcurrentUsers(1).to(users).during(130))
  ).protocols(httpProtocol)

}