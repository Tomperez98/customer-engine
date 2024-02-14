import Header from '@/components/Header'
import Table from '@/components/Table'
export default function Home() {
    return (
        <main>
            <Header />
            <div className='flex min-h-screen flex-col items-center p-8'>
                <h1>Flows</h1>
                <Table name='tomas' expertise='Backend' age={25} />
            </div>
        </main>
    )
}
