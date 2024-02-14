function Table({
    name,
    expertise,
    age,
}: {
    name: string
    expertise: string
    age: number
}) {
    const field1 = 'OtherPerson'
    return (
        <>
            <table className='table'>
                <thead>
                    <tr>
                        <th scope='col'>{field1}</th>
                        <th scope='col'>Most interest in</th>
                        <th scope='col'>Age</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th scope='row'>{name}</th>
                        <td>{expertise}</td>
                        <td>{age}</td>
                    </tr>
                </tbody>
            </table>
            <div>Pagination</div>
        </>
    )
}

export default Table
