import io.gatling.core.Predef._
import io.gatling.http.Predef._

class BasicSimulation extends Simulation {
  val httpProtocol = http.baseUrl("https://jsonplaceholder.typicode.com")

  val scn = scenario("Users API Smoke")
    .exec(http("get users")
      .get("/users")
      .check(status.is(200)))

  setUp(
    scn.inject(atOnceUsers(10))
  ).protocols(httpProtocol)
}
