'use client'
import {useState} from 'react'
import {Form} from '@/types/Forms'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

const useEditForm = (id: string, data: Form) => {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const {organization} = useKindeBrowserClient()

    const submit = async () => {
        setIsLoading(true)
        setError(null)
        try {
            Reflect.deleteProperty(data, 'automatic_response_id')
            const response = await fetch(`${BASE_URL}/${organization}/${id}`, {
                method: 'PATCH',
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

export default useEditForm
