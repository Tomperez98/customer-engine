import classNames from 'classnames'
import {motion} from 'framer-motion'

interface IconButtonProps {
    Icon: any
    onClick: () => void
    disabled?: boolean
    fill?: string
}

const IconButton = ({disabled, fill, Icon, onClick}: IconButtonProps) => {
    const animationProps = disabled
        ? {}
        : {
              whileHover: {scale: 1.1},
              whileTap: {scale: 0.9},
          }
    return (
        <motion.button
            className={classNames(fill || 'text-neutral-800')}
            onClick={onClick}
            {...animationProps}>
            <Icon />
        </motion.button>
    )
}

export default IconButton
