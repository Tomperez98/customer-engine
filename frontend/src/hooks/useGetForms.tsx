'use client'
import {useEffect, useState} from 'react'
import {Form} from '@/types/Forms'

type FormListResponse = {
    flows: Form[]
}

const useGetForms = (id?: string) => {
    const [data, setData] = useState<any>([])
    const [isLoading, setIsLoading] = useState<boolean>(false)

    const url = id
        ? `http://localhost:8000/ui/forms/${id}`
        : 'http://localhost:8000/ui/forms'

    const fetchForms = async () => {
        setIsLoading(true)
        try {
            const res = await fetch(url)
            const resJson = await res.json()
            console.log(resJson, 'here')
            setData(resJson)
        } catch (error) {
            console.log(error)
        } finally {
            setIsLoading(false)
        }
    }
    useEffect(() => {
        fetchForms()
    }, [])

    return {data, isLoading}
}

export default useGetForms
