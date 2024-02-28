'use client'
import {useState} from 'react'
import {Form} from '@/types/Forms'
import {BASE_URL} from '@/constants/url'

const useCreateForm = (data: any) => {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)

    const submit = async () => {
        setIsLoading(true)
        setError(null)
        try {
            const response = await fetch(BASE_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            setIsLoading(false)
            return await response.json()
        } catch (error: any) {
            setError(error)
            setIsLoading(false)
            throw error
        }
    }

    return {submit, isLoading, error}
}

export default useCreateForm
