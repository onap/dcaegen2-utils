/*
 * ================================================================================
 * Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
 * ================================================================================
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ============LICENSE_END=========================================================
 *
 */

package org.onap.dcae.utils.eelf.logger.api.log;


import org.onap.dcae.utils.eelf.logger.api.noop.NoOpEELFLogger;

import java.lang.reflect.InvocationTargetException;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.ServiceLoader;
import java.util.WeakHashMap;

/**
 * EELF Log Factory uses {@link ServiceLoader} to load implementations of {@link EELFLogger} in application
 * classpath. If no EELF Logging implementations are found - eelf logging is disabled and {@link NoOpEELFLogger}
 * is used.
 *
 * @author Rajiv Singla
 */
public class EELFLogFactory {

    private static final ServiceLoader<EELFLogger> SERVICE_LOADER = ServiceLoader.load(EELFLogger.class);
    private static final Map<Class<?>, EELFLogger> LOGGER_CACHE = new WeakHashMap<>(64);

    private static List<EELFLogger> loggerImplementations = new LinkedList<>();

    static {

        for (EELFLogger loggerImplementation : SERVICE_LOADER) {
            loggerImplementations.add(loggerImplementation);
        }

        if (loggerImplementations.isEmpty()) {
            System.err.println(
                    "EELF LOGGING ERROR: Unable to find any EELF Logger Implementations in the classpath.");
            System.err.println("=============EELF LOGGING IS DISABLED================");
            loggerImplementations.add(NoOpEELFLogger.getInstance());
        }

    }

    private EELFLogFactory() {
        // private constructor
    }

    public static <T> EELFLogger getLogger(Class<T> clazz) {

        if (LOGGER_CACHE.get(clazz) != null) {
            return LOGGER_CACHE.get(clazz);
        }

        EELFLogger EELFLogger = null;
        try {
            EELFLogger = loggerImplementations.get(0).getClass().getConstructor(Class.class)
                    .newInstance(clazz);
            return EELFLogger;

        } catch (
                InstantiationException | IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
            throw new IllegalStateException("Error while Creating EELF Logger", e);
        }

    }


}
