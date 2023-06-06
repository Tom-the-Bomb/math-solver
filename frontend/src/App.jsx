import NavBar from "./components/NavBar";
import Main from "./components/Main";
import Footer from "./components/Footer";

export default function App(props) {
  return (
    <div className="flex flex-col min-h-screen">
      <NavBar></NavBar>
      <Main></Main>
      <Footer></Footer>
    </div>
  );
}