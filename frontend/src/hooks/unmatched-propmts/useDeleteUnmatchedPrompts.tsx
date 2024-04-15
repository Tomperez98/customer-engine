'use client'
import {useState} from 'react'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

type PostBody = {
    prompt_ids: string[]
}

const useDeleteUnmatchedPrompts = () => {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const {accessTokenEncoded} = useKindeBrowserClient()

    const submit = async (data: PostBody) => {
        const headers = {
            'Authorization': `Bearer ${accessTokenEncoded}`,
            'Content-Type': 'application/json',
        }
        setIsLoading(true)
        setError(null)

        try {
            const response = await fetch(
                `${BASE_URL}/unmatched-prompts/delete`,
                {
                    method: 'POST',
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

export default useDeleteUnmatchedPrompts
