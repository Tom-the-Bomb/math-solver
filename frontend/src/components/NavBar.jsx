export default function NavBar() {
    return (
        <nav className="text-center bg-rose-900 font-serif p-6">
            <a title="info" className="float-left"
                href="https://github.com/Tom-the-Bomb/math-solver/blob/master/guide.md"
                target="_blank" rel="noreferrer"
            >
                <img className="h-7 hover:brightness-[120%] ease-in duration-150"
                    src={process.env.PUBLIC_URL + "/assets/question.svg"}
                    alt="(?)"/>
            </a>
            <a href="/" className="text-3xl text-white hover:brightness-90">
                Math ⋅ <span className="text-gray-300 text-2xl font-mono">
                    &lt;Solver&gt;
                </span>
            </a>
        </nav>
    )
}