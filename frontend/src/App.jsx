import NavBar from "./components/NavBar";
import Main from "./components/Main";
import Footer from "./components/Footer";
import { MathJaxContext } from "better-react-mathjax";

const BACKEND_HOST = !process.env.NODE_ENV || process.env.NODE_ENV.toLowerCase() === 'development'
    ? "http://localhost:5000"
    : "https://math-solver-api.tomthebomb.dev";

export default function App() {
    const mathJaxConfig = {
        loader: { load: ["input/asciimath"] }
    };

    return (
        <MathJaxContext config={mathJaxConfig}>
            <div className="flex flex-col min-h-screen">
                <NavBar></NavBar>
                <Main host={BACKEND_HOST}></Main>
                <Footer></Footer>
            </div>
        </MathJaxContext>
    );
}