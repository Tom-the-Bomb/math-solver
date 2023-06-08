import NavBar from "./components/NavBar";
import Main from "./components/Main";
import Footer from "./components/Footer";

const BACKEND_HOST = "http://127.0.0.1:5000";

export default function App() {
    return (
        <div className="flex flex-col min-h-screen">
            <NavBar></NavBar>
            <Main host={BACKEND_HOST}></Main>
            <Footer></Footer>
        </div>
    );
}