export default function NavBar() {
    return (
        <nav className="bg-rose-900 font-serif text-center p-6">
            <a href="/" className="text-3xl text-white hover:brightness-90">
                Math ⋅ <span className="text-gray-300 text-2xl font-mono">
                    &lt;Solver&gt;
                </span>
            </a>
        </nav>
    )
}