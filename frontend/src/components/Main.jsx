function Input({placeholder}) {
    return (
        <textarea
            className="font-serif w-full placeholder:italic placeholder:text-slate-400
            bg-white border border-slate-300
            py-2 pl-3 pr-3 shadow-sm focus:outline-none
            focus:border-sky-500 focus:ring-sky-500 focus:ring-1 sm:text-sm"
            placeholder={placeholder}
            type="text"
            name="search"
            spellCheck="false"
            autoCorrect="false"
            autoCapitalize="false"
            data-gramm="false" data-gramm_editor="false" data-enable-grammarly="false"
        />
    )
}

function Form() {
    function handleSubmit(event) {
        event.preventDefault()
    }

    return (
        <form className="w-full" onSubmit={handleSubmit}>
            <label class="relative block">
            <span class="sr-only">Search</span>
            <Input placeholder={"Enter an equation..."}></Input>
            </label>
        </form>
    )
}

export default function Main(props) {
    return (
        <main className="grow grid grid-cols-2">
            <div className="bg-red-1 drop-shadow-2xl flex flex-column items-center">
                <Form></Form>
            </div>
            <div className="bg-red-2">
                
            </div>
        </main>
    )
}