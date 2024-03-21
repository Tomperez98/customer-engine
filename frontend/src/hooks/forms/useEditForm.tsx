'use client'
import {useState} from 'react'
import {Form} from '@/types/Forms'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

const useEditForm = (id: string, data: Form) => {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const {accessTokenEncoded} = useKindeBrowserClient()

    const submit = async () => {
        const headers = {
            'Authorization': `Bearer ${accessTokenEncoded}`,
            'Content-Type': 'application/json',
        }
        setIsLoading(true)
        setError(null)
        try {
            Reflect.deleteProperty(data, 'automatic_response_id')
            const response = await fetch(
                `${BASE_URL}/automatic-responses/${id}`,
                {
                    method: 'PATCH',
                    headers: headers,
                    body: JSON.stringify(data),
                }
            )
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
